from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from app.contracts import InstrumentOutputEvent, PlaybackEvent


def map_to_playback_event(
    event: InstrumentOutputEvent,
    raw_payload: dict[str, Any],
    emitted_at: datetime | None = None,
) -> PlaybackEvent:
    scheduled_beat_time = _scheduled_beat_time(raw_payload)
    current_time = emitted_at or datetime.now(UTC)

    return PlaybackEvent(
        playback_id=uuid4(),
        note_id=event.note_id,
        instrument=event.instrument,
        pitch=event.audio_hint.pitch,
        duration=event.audio_hint.duration,
        volume=event.audio_hint.volume,
        scheduled_beat_time=scheduled_beat_time,
        emitted_at=current_time,
    )


def calculate_latency_ms(rendered_at: datetime, emitted_at: datetime) -> float:
    return max(0.0, (emitted_at - rendered_at).total_seconds() * 1000.0)


def _scheduled_beat_time(raw_payload: dict[str, Any]) -> float:
    for key in ("scheduled_beat_time", "beat_time"):
        value = raw_payload.get(key)
        if isinstance(value, int | float):
            return float(value)
    return 0.0
