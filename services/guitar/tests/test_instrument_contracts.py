from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from services.instruments_shared.contracts import NoteEvent


def test_note_event_validates_and_normalizes_timestamp() -> None:
    event = NoteEvent.model_validate(
        {
            "note_id": "n-1",
            "session_id": "s-1",
            "instrument": "guitar",
            "pitch": 60,
            "duration": 0.5,
            "volume": 100,
            "beat_time": 1.25,
            "timestamp": "2026-04-06T10:10:00Z",
        }
    )

    assert event.timestamp == datetime(2026, 4, 6, 10, 10, 0, tzinfo=UTC)


def test_note_event_rejects_invalid_pitch() -> None:
    with pytest.raises(ValidationError):
        NoteEvent.model_validate(
            {
                "note_id": "n-2",
                "instrument": "guitar",
                "pitch": 200,
                "duration": 0.5,
                "volume": 100,
                "beat_time": 1.25,
                "timestamp": "2026-04-06T10:10:00Z",
            }
        )
