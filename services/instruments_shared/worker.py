from __future__ import annotations

import json
import logging
import time
from datetime import UTC, datetime
from typing import Any, Mapping

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import AMQPError
from prometheus_client import Counter
from pydantic import ValidationError

from .config import InstrumentSettings
from .contracts import InstrumentOutputEvent, NoteEvent
from .topology import dead_letter_queue_name, dead_letter_routing_key

LOGGER = logging.getLogger(__name__)
BACKOFF_SECONDS = (1, 2, 5, 10)

MESSAGES_RECEIVED = Counter(
    "instrument_messages_received_total",
    "Total messages received by instrument worker",
    ["service", "instrument"],
)
MESSAGES_PROCESSED = Counter(
    "instrument_messages_processed_total",
    "Total messages successfully processed by instrument worker",
    ["service", "instrument"],
)
MESSAGES_FAILED = Counter(
    "instrument_messages_failed_total",
    "Total messages failed by instrument worker",
    ["service", "instrument"],
)
DUPLICATE_MESSAGES = Counter(
    "instrument_messages_duplicate_total",
    "Total duplicate messages skipped by instrument worker",
    ["service", "instrument"],
)


class InstrumentWorker:
    def __init__(self, settings: InstrumentSettings) -> None:
        self._settings = settings
        self._connection: pika.BlockingConnection | None = None
        self._channel: BlockingChannel | None = None
        self._processed_note_ids: set[str] = set()
        self._running = False

    def metrics_snapshot(self) -> dict[str, int]:
        return {
            "received": int(
                MESSAGES_RECEIVED.labels(
                    self._settings.service_name, self._settings.instrument_name
                )._value.get()
            ),
            "processed": int(
                MESSAGES_PROCESSED.labels(
                    self._settings.service_name, self._settings.instrument_name
                )._value.get()
            ),
            "failed": int(
                MESSAGES_FAILED.labels(
                    self._settings.service_name, self._settings.instrument_name
                )._value.get()
            ),
            "duplicates": int(
                DUPLICATE_MESSAGES.labels(
                    self._settings.service_name, self._settings.instrument_name
                )._value.get()
            ),
        }

    def start(self) -> None:
        self._running = True
        while self._running:
            try:
                self._connect()
                if not self._running:
                    break
                assert self._channel is not None
                self._channel.start_consuming()
            except RuntimeError as exc:
                if str(exc) == "worker_stopped":
                    break
                raise
            except AMQPError as exc:
                LOGGER.warning(
                    "consumer_disconnected",
                    extra={"service": self._settings.service_name, "error": str(exc)},
                )
                self._safe_close()
                self._sleep_with_backoff(0)
            except Exception:
                LOGGER.exception("consumer_crashed", extra={"service": self._settings.service_name})
                self._safe_close()
                self._sleep_with_backoff(0)

    def stop(self) -> None:
        self._running = False
        self._safe_close()

    def process_body(
        self, body: bytes, headers: Mapping[str, Any] | None = None
    ) -> tuple[str, str]:
        MESSAGES_RECEIVED.labels(self._settings.service_name, self._settings.instrument_name).inc()
        LOGGER.info(
            "message_received",
            extra={
                "service": self._settings.service_name,
                "instrument": self._settings.instrument_name,
            },
        )

        note_event = self._parse_note_event(body)
        if note_event is None:
            MESSAGES_FAILED.labels(
                self._settings.service_name, self._settings.instrument_name
            ).inc()
            return "discard", "invalid_payload"

        if note_event.instrument != self._settings.instrument_name:
            LOGGER.error(
                "message_instrument_mismatch",
                extra={
                    "service": self._settings.service_name,
                    "instrument": self._settings.instrument_name,
                    "received_instrument": note_event.instrument,
                    "note_id": note_event.note_id,
                },
            )
            MESSAGES_FAILED.labels(
                self._settings.service_name, self._settings.instrument_name
            ).inc()
            return "discard", "instrument_mismatch"

        if self._is_duplicate(note_event.note_id):
            DUPLICATE_MESSAGES.labels(
                self._settings.service_name, self._settings.instrument_name
            ).inc()
            LOGGER.info(
                "message_duplicate",
                extra={
                    "service": self._settings.service_name,
                    "instrument": self._settings.instrument_name,
                    "note_id": note_event.note_id,
                },
            )
            return "ack", "duplicate"

        try:
            output_event = self._build_output_event(note_event)
            self._publish_output(output_event)
        except AMQPError:
            LOGGER.exception(
                "message_publish_failed",
                extra={
                    "service": self._settings.service_name,
                    "instrument": self._settings.instrument_name,
                    "note_id": note_event.note_id,
                },
            )
            MESSAGES_FAILED.labels(
                self._settings.service_name, self._settings.instrument_name
            ).inc()
            if self._should_retry(headers):
                return "retry", "publish_failed"
            return "dlq", "publish_failed"
        except Exception:
            LOGGER.exception(
                "message_process_failed",
                extra={
                    "service": self._settings.service_name,
                    "instrument": self._settings.instrument_name,
                    "note_id": note_event.note_id,
                },
            )
            MESSAGES_FAILED.labels(
                self._settings.service_name, self._settings.instrument_name
            ).inc()
            if self._should_retry(headers):
                return "retry", "processing_failed"
            return "dlq", "processing_failed"

        self._remember(note_event.note_id)
        MESSAGES_PROCESSED.labels(self._settings.service_name, self._settings.instrument_name).inc()
        LOGGER.info(
            "message_processed",
            extra={
                "service": self._settings.service_name,
                "instrument": self._settings.instrument_name,
                "note_id": note_event.note_id,
            },
        )
        return "ack", "ok"

    def _connect(self) -> None:
        attempt = 0
        while self._running:
            try:
                self._connection = pika.BlockingConnection(
                    pika.URLParameters(self._settings.rabbitmq_url)
                )
                self._channel = self._connection.channel()
                self._channel.confirm_delivery()
                self._channel.exchange_declare(
                    exchange=self._settings.exchange_name,
                    exchange_type="topic",
                    durable=True,
                )

                dlq_name = dead_letter_queue_name(self._settings.input_queue)
                self._channel.queue_declare(queue=dlq_name, durable=True)
                self._channel.queue_bind(
                    exchange=self._settings.exchange_name,
                    queue=dlq_name,
                    routing_key=dead_letter_routing_key(self._settings.input_queue),
                )

                queue_arguments = {
                    "x-dead-letter-exchange": self._settings.exchange_name,
                    "x-dead-letter-routing-key": dead_letter_routing_key(
                        self._settings.input_queue
                    ),
                }
                self._channel.queue_declare(
                    queue=self._settings.input_queue,
                    durable=True,
                    arguments=queue_arguments,
                )
                self._channel.queue_bind(
                    exchange=self._settings.exchange_name,
                    queue=self._settings.input_queue,
                    routing_key=self._settings.input_queue,
                )
                self._channel.basic_qos(prefetch_count=self._settings.prefetch_count)
                self._channel.basic_consume(
                    queue=self._settings.input_queue,
                    on_message_callback=self._on_message,
                    auto_ack=False,
                )

                LOGGER.info(
                    "rabbitmq_connected",
                    extra={
                        "service": self._settings.service_name,
                        "instrument": self._settings.instrument_name,
                        "input_queue": self._settings.input_queue,
                        "output_routing_key": self._settings.output_routing_key,
                    },
                )
                return
            except AMQPError as exc:
                delay = BACKOFF_SECONDS[min(attempt, len(BACKOFF_SECONDS) - 1)]
                attempt += 1
                LOGGER.warning(
                    "rabbitmq_connect_retry",
                    extra={
                        "service": self._settings.service_name,
                        "delay_seconds": delay,
                        "error": str(exc),
                    },
                )
                time.sleep(delay)

        raise RuntimeError("worker_stopped")

    def _on_message(
        self,
        channel: BlockingChannel,
        method: Any,
        properties: pika.BasicProperties,
        body: bytes,
    ) -> None:
        headers = properties.headers if properties.headers is not None else None
        if headers is not None and not isinstance(headers, dict):
            headers = dict(headers)

        action, reason = self.process_body(body=body, headers=headers)
        LOGGER.info(
            "message_result",
            extra={
                "service": self._settings.service_name,
                "instrument": self._settings.instrument_name,
                "delivery_tag": method.delivery_tag,
                "action": action,
                "reason": reason,
            },
        )
        if action == "ack":
            channel.basic_ack(delivery_tag=method.delivery_tag)
            return
        if action == "retry":
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            return
        if action in {"discard", "dlq"}:
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return

        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def _parse_note_event(self, body: bytes) -> NoteEvent | None:
        try:
            raw = json.loads(body.decode("utf-8"))
            return NoteEvent.model_validate(raw)
        except (UnicodeDecodeError, json.JSONDecodeError, ValidationError) as exc:
            LOGGER.error(
                "invalid_note_event",
                extra={
                    "service": self._settings.service_name,
                    "instrument": self._settings.instrument_name,
                    "error": str(exc),
                },
            )
            return None

    def _build_output_event(self, note_event: NoteEvent) -> InstrumentOutputEvent:
        rendered_at = datetime.now(UTC)
        latency_ms = max(0, int((rendered_at - note_event.timestamp).total_seconds() * 1000))
        return InstrumentOutputEvent(
            note_id=note_event.note_id,
            instrument=self._settings.instrument_name,
            beat_time=note_event.beat_time,
            rendered_at=rendered_at,
            latency_ms=latency_ms,
            audio_hint={
                "pitch": note_event.pitch,
                "duration": note_event.duration,
                "volume": note_event.volume,
            },
        )

    def _publish_output(self, output_event: InstrumentOutputEvent) -> None:
        if self._channel is None or self._connection is None or self._connection.is_closed:
            self._connect()
        assert self._channel is not None

        payload = output_event.model_dump(mode="json")
        properties = pika.BasicProperties(content_type="application/json", delivery_mode=2)
        self._channel.basic_publish(
            exchange=self._settings.exchange_name,
            routing_key=self._settings.output_routing_key,
            body=json.dumps(payload).encode("utf-8"),
            properties=properties,
            mandatory=False,
        )

    def _should_retry(self, headers: Mapping[str, Any] | None) -> bool:
        retry_count = self._extract_retry_count(headers)
        return retry_count < self._settings.max_retries

    def _extract_retry_count(self, headers: Mapping[str, Any] | None) -> int:
        if not headers:
            return 0

        x_death = headers.get("x-death")
        if isinstance(x_death, list) and x_death:
            first = x_death[0]
            if isinstance(first, dict):
                count = first.get("count")
                if isinstance(count, int):
                    return count
                if isinstance(count, float):
                    return int(count)
        return 0

    def _remember(self, note_id: str) -> None:
        self._processed_note_ids.add(note_id)

    def _is_duplicate(self, note_id: str) -> bool:
        return note_id in self._processed_note_ids

    def _safe_close(self) -> None:
        try:
            if self._connection is not None and self._connection.is_open:
                self._connection.close()
        except Exception:  # noqa: BLE001
            LOGGER.warning(
                "worker_connection_close_failed",
                extra={"service": self._settings.service_name},
            )
        self._connection = None
        self._channel = None

    def _sleep_with_backoff(self, attempt: int) -> None:
        delay = BACKOFF_SECONDS[min(attempt, len(BACKOFF_SECONDS) - 1)]
        time.sleep(delay)
