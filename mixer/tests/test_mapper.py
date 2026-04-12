from datetime import UTC, datetime
from uuid import uuid4

from app.contracts import AudioHint, InstrumentOutputEvent
from app.mapper import calculate_latency_ms, map_to_playback_event


def test_map_to_playback_event_uses_audio_hint_and_scheduled_beat_time() -> None:
    note_id = uuid4()
    rendered_at = datetime(2026, 4, 6, 10, 10, 0, tzinfo=UTC)
    emitted_at = datetime(2026, 4, 6, 10, 10, 0, 120000, tzinfo=UTC)

    event = InstrumentOutputEvent(
        note_id=note_id,
        instrument="guitar",
        rendered_at=rendered_at,
        latency_ms=35,
        audio_hint=AudioHint(pitch=64, duration=0.5, volume=90),
    )
    raw_payload = {"scheduled_beat_time": 12.5}

    playback = map_to_playback_event(event, raw_payload=raw_payload, emitted_at=emitted_at)

    assert playback.note_id == note_id
    assert playback.instrument == "guitar"
    assert playback.pitch == 64
    assert playback.duration == 0.5
    assert playback.volume == 90
    assert playback.scheduled_beat_time == 12.5
    assert playback.emitted_at == emitted_at


def test_map_to_playback_event_supports_beat_time_fallback() -> None:
    event = InstrumentOutputEvent(
        note_id=uuid4(),
        instrument="drums",
        rendered_at=datetime(2026, 4, 6, 10, 10, 0, tzinfo=UTC),
        latency_ms=10,
        audio_hint=AudioHint(pitch=36, duration=0.25, volume=120),
    )

    playback = map_to_playback_event(event, raw_payload={"beat_time": 3.5})
    assert playback.scheduled_beat_time == 3.5


def test_calculate_latency_ms_never_negative() -> None:
    rendered_at = datetime(2026, 4, 6, 10, 10, 1, tzinfo=UTC)
    emitted_at = datetime(2026, 4, 6, 10, 10, 0, tzinfo=UTC)
    assert calculate_latency_ms(rendered_at, emitted_at) == 0.0
