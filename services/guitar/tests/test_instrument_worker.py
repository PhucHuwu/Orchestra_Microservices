from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

import pika

from services.instruments_shared import InstrumentSettings, InstrumentWorker


def make_settings() -> InstrumentSettings:
    return InstrumentSettings(
        SERVICE_NAME="guitar-service",
        INSTRUMENT_NAME="guitar",
        INPUT_QUEUE="instrument.guitar.note",
        OUTPUT_ROUTING_KEY="instrument.guitar.output",
        MAX_RETRIES=3,
    )


def make_note_payload(note_id: str = "note-1") -> bytes:
    payload = {
        "note_id": note_id,
        "session_id": "session-1",
        "instrument": "guitar",
        "pitch": 60,
        "duration": 0.5,
        "volume": 100,
        "beat_time": 1.25,
        "timestamp": datetime.now(UTC).isoformat(),
    }
    return json.dumps(payload).encode("utf-8")


def test_process_body_success_ack(monkeypatch: Any) -> None:
    worker = InstrumentWorker(make_settings())
    published: list[dict[str, Any]] = []

    def fake_publish(output_event: Any) -> None:
        published.append(output_event.model_dump(mode="json"))

    monkeypatch.setattr(worker, "_publish_output", fake_publish)

    action, reason = worker.process_body(make_note_payload())

    assert action == "ack"
    assert reason == "ok"
    assert len(published) == 1
    assert published[0]["instrument"] == "guitar"
    assert published[0]["audio_hint"]["pitch"] == 60


def test_process_body_duplicate_ack_without_publish(monkeypatch: Any) -> None:
    worker = InstrumentWorker(make_settings())
    call_count = {"published": 0}

    def fake_publish(_: Any) -> None:
        call_count["published"] += 1

    monkeypatch.setattr(worker, "_publish_output", fake_publish)

    first_action, first_reason = worker.process_body(make_note_payload("dup-1"))
    second_action, second_reason = worker.process_body(make_note_payload("dup-1"))

    assert first_action == "ack"
    assert first_reason == "ok"
    assert second_action == "ack"
    assert second_reason == "duplicate"
    assert call_count["published"] == 1


def test_process_body_invalid_payload_discard() -> None:
    worker = InstrumentWorker(make_settings())

    action, reason = worker.process_body(b"not-json")

    assert action == "discard"
    assert reason == "invalid_payload"


def test_process_body_publish_failure_retry_or_dlq(monkeypatch: Any) -> None:
    worker = InstrumentWorker(make_settings())

    def fake_publish(_: Any) -> None:
        raise pika.exceptions.AMQPError("publish failed")

    monkeypatch.setattr(worker, "_publish_output", fake_publish)

    retry_action, retry_reason = worker.process_body(
        make_note_payload("retry-1"),
        headers={"x-death": [{"count": 1}]},
    )
    dlq_action, dlq_reason = worker.process_body(
        make_note_payload("retry-2"),
        headers={"x-death": [{"count": 3}]},
    )

    assert retry_action == "retry"
    assert retry_reason == "publish_failed"
    assert dlq_action == "dlq"
    assert dlq_reason == "publish_failed"


def test_on_message_acks_only_after_success(monkeypatch: Any) -> None:
    worker = InstrumentWorker(make_settings())
    monkeypatch.setattr(worker, "process_body", lambda *_args, **_kwargs: ("ack", "ok"))

    class StubChannel:
        def __init__(self) -> None:
            self.acks: list[int] = []
            self.nacks: list[tuple[int, bool]] = []

        def basic_ack(self, delivery_tag: int) -> None:
            self.acks.append(delivery_tag)

        def basic_nack(self, delivery_tag: int, requeue: bool) -> None:
            self.nacks.append((delivery_tag, requeue))

    class StubMethod:
        delivery_tag = 7

    channel = StubChannel()
    properties = pika.BasicProperties(headers={})
    worker._on_message(channel, StubMethod(), properties, make_note_payload("ack-1"))

    assert channel.acks == [7]
    assert channel.nacks == []
