from __future__ import annotations

import json
import logging
import threading
import time
from datetime import UTC, datetime
from typing import Any

from pika.exceptions import AMQPError
from pydantic import ValidationError

from app.config import Settings
from app.contracts import InstrumentOutputEvent
from app.mapper import calculate_latency_ms, map_to_playback_event
from app.messaging.rabbitmq import RabbitMQClient
from app.metrics import (
    LATENCY_MS,
    MAPPING_ERRORS_TOTAL,
    MESSAGES_PROCESSED_TOTAL,
    PUBLISH_ERRORS_TOTAL,
)

LOGGER = logging.getLogger(__name__)
MAX_RETRY_COUNT = 3


class MixerWorker:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = RabbitMQClient(settings)
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._requeue_attempts: dict[str, int] = {}

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        self._client.close()

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def _run(self) -> None:
        self._client.connect()
        while not self._stop_event.is_set():
            try:
                method, properties, body = self._client.basic_get(self._settings.input_queue)
            except AMQPError:
                LOGGER.exception("mixer_consume_failed")
                time.sleep(0.5)
                continue

            if method is None or body is None:
                time.sleep(0.05)
                continue

            retry_count = self._extract_retry_count(properties)
            try:
                self._process_message(method.delivery_tag, body, retry_count)
            except Exception:  # noqa: BLE001
                LOGGER.exception("mixer_unhandled_processing_error")
                time.sleep(0.2)

    def _process_message(self, delivery_tag: int, body: bytes, retry_count: int) -> None:
        raw_payload: dict[str, Any] = {}
        instrument_label = "unknown"
        note_id = "unknown"

        try:
            raw_payload = json.loads(body)
            event = InstrumentOutputEvent.model_validate(raw_payload)
            instrument_label = event.instrument
            note_id = str(event.note_id)

            emitted_at = datetime.now(UTC)
            playback = map_to_playback_event(event, raw_payload=raw_payload, emitted_at=emitted_at)

            self._client.publish_json(
                routing_key=self._settings.output_routing_key,
                payload=playback.model_dump(mode="json"),
            )

            self._client.ack(delivery_tag)

            latency_ms = calculate_latency_ms(event.rendered_at, emitted_at)
            LATENCY_MS.labels(instrument=instrument_label).observe(latency_ms)
            MESSAGES_PROCESSED_TOTAL.labels(instrument=instrument_label).inc()

            LOGGER.info(
                "mixer_message_processed",
                extra={
                    "note_id": note_id,
                    "instrument": instrument_label,
                    "latency_ms": latency_ms,
                },
            )
            self._requeue_attempts.pop(note_id, None)
            return
        except (json.JSONDecodeError, ValidationError):
            MAPPING_ERRORS_TOTAL.labels(instrument=instrument_label).inc()
            LOGGER.exception("mixer_message_invalid")
            self._client.nack(delivery_tag, requeue=False)
            return
        except AMQPError:
            PUBLISH_ERRORS_TOTAL.labels(instrument=instrument_label).inc()
            LOGGER.exception("mixer_publish_failed")

        current_retries = self._requeue_attempts.get(note_id, retry_count)
        if current_retries < MAX_RETRY_COUNT:
            self._requeue_attempts[note_id] = current_retries + 1
            self._client.nack(delivery_tag, requeue=True)
            return

        self._requeue_attempts.pop(note_id, None)
        self._client.nack(delivery_tag, requeue=False)

    def _extract_retry_count(self, properties: Any) -> int:
        headers = getattr(properties, "headers", None)
        if not isinstance(headers, dict):
            return 0
        try:
            return int(headers.get("x-retry-count", 0))
        except (TypeError, ValueError):
            return 0
