from __future__ import annotations

import time
from datetime import datetime, timezone
from uuid import uuid4

from app.config import Settings
from app.models import ConductorStartRequest, ParsedNote, TempoCommand
from app.service import ConductorRuntime


class _FakePublisher:
    def __init__(self) -> None:
        self.published: list[tuple[str, dict]] = []

    def connect(self) -> None:
        return

    def close(self) -> None:
        return

    def publish_json(self, routing_key: str, payload: dict) -> None:
        self.published.append((routing_key, payload))


def _make_runtime() -> ConductorRuntime:
    settings = Settings(
        RABBITMQ_URL="amqp://guest:guest@localhost:5672/%2F",
        SCORE_DIR="scores",
        HEARTBEAT_INTERVAL_SECONDS=0.05,
    )
    runtime = ConductorRuntime(settings)
    runtime._publisher = _FakePublisher()  # type: ignore[attr-defined]
    return runtime


def test_scheduler_publishes_ordered_routing_keys() -> None:
    runtime = _make_runtime()
    session_id = uuid4()

    runtime._notes = [  # type: ignore[attr-defined]
        ParsedNote(instrument="guitar", pitch=64, duration=1.0, volume=90, beat_position=0.0),
        ParsedNote(instrument="guitar", pitch=65, duration=1.0, volume=91, beat_position=1.0),
        ParsedNote(instrument="drums", pitch=36, duration=0.5, volume=110, beat_position=1.5),
    ]
    runtime._bpm = 10000  # type: ignore[attr-defined]
    runtime._status.status = "running"  # type: ignore[attr-defined]
    runtime._status.session_id = session_id  # type: ignore[attr-defined]

    runtime._run_scheduler()  # type: ignore[attr-defined]

    published = runtime._publisher.published  # type: ignore[attr-defined]
    routing_keys = [item[0] for item in published]
    assert routing_keys == [
        "instrument.guitar.note",
        "instrument.guitar.note",
        "instrument.drums.beat",
    ]
    assert runtime.status().published_notes == 3


def test_tempo_update_while_running(monkeypatch) -> None:
    runtime = _make_runtime()
    session_id = uuid4()

    notes = [
        ParsedNote(instrument="guitar", pitch=60, duration=1.0, volume=100, beat_position=0.0),
        ParsedNote(instrument="oboe", pitch=62, duration=1.0, volume=100, beat_position=1.0),
    ]

    monkeypatch.setattr("app.service.parse_midi_file", lambda *_args, **_kwargs: notes)
    monkeypatch.setattr("app.service.ConductorRuntime._run_heartbeat", lambda self: None)
    monkeypatch.setattr(
        "app.service.ConductorRuntime._consume_tempo_commands",
        lambda self: self._stop_event.wait(timeout=0.2),
    )

    start_req = ConductorStartRequest(score_path="dummy.mid", initial_bpm=60, session_id=session_id)
    runtime.start(start_req)

    command = TempoCommand(
        session_id=session_id,
        new_bpm=180,
        issued_by="dashboard",
        issued_at=datetime.now(timezone.utc),
    )
    runtime.set_tempo(command)
    time.sleep(0.05)
    status = runtime.status()
    runtime.stop(session_id)

    assert status.status in {"running", "stopped"}
    assert status.bpm == 180
    assert status.session_id == session_id

