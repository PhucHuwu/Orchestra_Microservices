from __future__ import annotations

import logging
import threading
import time
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

import httpx
import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import AMQPError

from app.config import Settings
from app.messaging.rabbitmq import RabbitMQPublisher, create_tempo_consumer_channel
from app.midi_parser import parse_midi_file
from app.models import (
    ConductorStartRequest,
    ConductorStatus,
    NoteEvent,
    ParsedNote,
    TempoCommand,
    routing_key_for_instrument,
)

LOGGER = logging.getLogger(__name__)

SERVICE_ENDPOINTS = {
    "guitar-service": "guitar_service_url",
    "oboe-service": "oboe_service_url",
    "drums-service": "drums_service_url",
}


class ConductorRuntime:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._publisher = RabbitMQPublisher(settings)
        self._lock = threading.RLock()
        self._status = ConductorStatus(status="stopped")
        self._stop_event = threading.Event()
        self._worker_thread: threading.Thread | None = None
        self._tempo_thread: threading.Thread | None = None
        self._heartbeat_thread: threading.Thread | None = None
        self._notes: list[ParsedNote] = []
        self._bpm = 120
        self._enabled = True

    def start(self, request: ConductorStartRequest) -> ConductorStatus:
        with self._lock:
            if not self._enabled:
                raise RuntimeError("conductor_disabled")
            if self._status.status == "running":
                return self._status

            self._notes = parse_midi_file(request.score_path, self._settings.score_dir)
            self._bpm = request.initial_bpm
            self._status = ConductorStatus(
                status="running",
                session_id=request.session_id,
                bpm=self._bpm,
                total_notes=len(self._notes),
            )
            self._stop_event.clear()

            self._publisher.connect()

            self._worker_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self._tempo_thread = threading.Thread(target=self._consume_tempo_commands, daemon=True)
            self._heartbeat_thread = threading.Thread(target=self._run_heartbeat, daemon=True)

            self._worker_thread.start()
            self._tempo_thread.start()
            self._heartbeat_thread.start()

            LOGGER.info(
                "conductor_started",
                extra={
                    "session_id": str(request.session_id),
                    "initial_bpm": request.initial_bpm,
                    "total_notes": len(self._notes),
                },
            )
            return self._status

    def stop(self, session_id: UUID | None = None) -> ConductorStatus:
        with self._lock:
            if self._status.status != "running":
                return self._status

            if session_id is not None and self._status.session_id != session_id:
                return self._status

            self._stop_event.set()
            self._status.status = "stopped"
            LOGGER.info(
                "conductor_stopped",
                extra={
                    "session_id": str(self._status.session_id) if self._status.session_id else None
                },
            )

        self._publisher.close()
        return self._status

    def status(self) -> ConductorStatus:
        with self._lock:
            return self._status.model_copy(deep=True)

    def set_enabled(self, enabled: bool) -> bool:
        with self._lock:
            self._enabled = enabled
            if not enabled and self._status.status == "running":
                self._stop_event.set()
                self._status.status = "stopped"
        if not enabled:
            self._publisher.close()
        return self._enabled

    def is_enabled(self) -> bool:
        with self._lock:
            return self._enabled

    def set_tempo(self, command: TempoCommand) -> ConductorStatus:
        with self._lock:
            if self._status.session_id != command.session_id:
                return self._status
            old_bpm = self._bpm
            self._bpm = command.new_bpm
            self._status.bpm = command.new_bpm

        LOGGER.info(
            "tempo_updated",
            extra={
                "session_id": str(command.session_id),
                "old_bpm": old_bpm,
                "new_bpm": command.new_bpm,
                "issued_at": command.issued_at.isoformat(),
                "issued_by": command.issued_by,
            },
        )
        return self.status()

    def service_control_status(self) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        with httpx.Client(timeout=3.0) as client:
            for service_name, url_attr in SERVICE_ENDPOINTS.items():
                base_url = str(getattr(self._settings, url_attr)).rstrip("/")
                enabled = False
                running = False
                reachable = False
                message: str | None = None
                try:
                    response = client.get(f"{base_url}/control/worker")
                    if response.status_code < 400:
                        payload = response.json()
                        if isinstance(payload, dict):
                            enabled = bool(payload.get("enabled", False))
                            running = bool(payload.get("running", False))
                        reachable = True
                except Exception as exc:  # noqa: BLE001
                    message = str(exc)
                items.append(
                    {
                        "service_name": service_name,
                        "enabled": enabled,
                        "running": running,
                        "reachable": reachable,
                        "message": message,
                    }
                )
        return items

    def set_service_enabled(self, service_name: str, enabled: bool) -> dict[str, Any]:
        if service_name not in SERVICE_ENDPOINTS:
            raise ValueError(f"Unsupported service: {service_name}")

        base_url = str(getattr(self._settings, SERVICE_ENDPOINTS[service_name])).rstrip("/")
        action = "start" if enabled else "stop"
        with httpx.Client(timeout=6.0) as client:
            response = client.post(f"{base_url}/control/worker/{action}")
            response.raise_for_status()
            payload = response.json()

        result = {
            "service_name": service_name,
            "enabled": bool(payload.get("enabled", enabled)) if isinstance(payload, dict) else enabled,
            "running": bool(payload.get("running", enabled)) if isinstance(payload, dict) else enabled,
        }
        LOGGER.info(
            "instrument_service_toggled",
            extra={
                "service_name": service_name,
                "enabled": result["enabled"],
                "running": result["running"],
            },
        )
        return result

    def _run_scheduler(self) -> None:
        with self._lock:
            status = self._status.model_copy(deep=True)

        if status.session_id is None:
            return

        previous_beat = 0.0
        try:
            for note in self._notes:
                if self._stop_event.is_set():
                    break

                delta_beats = max(0.0, note.beat_position - previous_beat)
                previous_beat = note.beat_position
                sleep_seconds = self._beats_to_seconds(delta_beats)
                self._stop_event.wait(timeout=sleep_seconds)
                if self._stop_event.is_set():
                    break

                event = NoteEvent(
                    session_id=status.session_id,
                    instrument=note.instrument,
                    pitch=note.pitch,
                    duration=self._beats_to_seconds(note.duration),
                    volume=note.volume,
                    beat_time=note.beat_position,
                )
                routing_key = routing_key_for_instrument(note.instrument)
                self._publisher.publish_json(
                    routing_key=routing_key, payload=event.model_dump(mode="json")
                )

                with self._lock:
                    self._status.published_notes += 1

            with self._lock:
                if self._status.status == "running":
                    self._status.status = "stopped"
        except Exception as exc:  # noqa: BLE001
            LOGGER.exception("scheduler_failed")
            with self._lock:
                self._status.status = "failed"
                self._status.last_error = str(exc)

    def _run_heartbeat(self) -> None:
        while not self._stop_event.is_set():
            current_status = self.status()
            if current_status.session_id is not None:
                heartbeat = {
                    "service": self._settings.service_name,
                    "session_id": str(current_status.session_id),
                    "status": current_status.status,
                    "published_notes": current_status.published_notes,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                try:
                    self._publisher.publish_json(self._settings.heartbeat_queue, heartbeat)
                except AMQPError:
                    LOGGER.exception("heartbeat_publish_failed")
            self._stop_event.wait(timeout=self._settings.heartbeat_interval_seconds)

    def _consume_tempo_commands(self) -> None:
        connection = None
        channel = None
        try:
            connection, channel = create_tempo_consumer_channel(self._settings)
            while not self._stop_event.is_set():
                method, properties, body = channel.basic_get(
                    queue=self._settings.tempo_control_queue,
                    auto_ack=False,
                )
                if method is None:
                    time.sleep(0.2)
                    continue

                try:
                    command = TempoCommand.model_validate_json(body)
                    self.set_tempo(command)
                    channel.basic_ack(delivery_tag=method.delivery_tag)
                except Exception:  # noqa: BLE001
                    LOGGER.exception("tempo_command_invalid")
                    retry_count = self._extract_retry_count(properties)
                    if retry_count < 3:
                        self._republish_tempo(channel, body, retry_count + 1)
                        channel.basic_ack(delivery_tag=method.delivery_tag)
                    else:
                        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except AMQPError:
            LOGGER.exception("tempo_consumer_failed")
        finally:
            if channel is not None and channel.is_open:
                channel.close()
            if connection is not None and connection.is_open:
                connection.close()

    def _beats_to_seconds(self, beats: float) -> float:
        with self._lock:
            bpm = self._bpm
        return (60.0 / bpm) * beats

    def _extract_retry_count(self, properties: Any) -> int:
        headers = getattr(properties, "headers", None)
        if not isinstance(headers, dict):
            return 0
        try:
            return int(headers.get("x-retry-count", 0))
        except (TypeError, ValueError):
            return 0

    def _republish_tempo(self, channel: BlockingChannel, body: bytes, retry_count: int) -> None:
        channel.basic_publish(
            exchange=self._settings.exchange_name,
            routing_key=self._settings.tempo_control_queue,
            body=body,
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=2,
                headers={"x-retry-count": retry_count},
            ),
        )
