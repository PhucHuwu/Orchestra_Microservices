from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class NoteEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")

    note_id: str
    session_id: str | None = None
    instrument: str
    pitch: int = Field(ge=0, le=127)
    duration: float = Field(gt=0)
    volume: int = Field(ge=0, le=127)
    beat_time: float
    timestamp: datetime

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, value: datetime | str) -> datetime:
        parsed = (
            value
            if isinstance(value, datetime)
            else datetime.fromisoformat(value.replace("Z", "+00:00"))
        )
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC)


class AudioHint(BaseModel):
    pitch: int = Field(ge=0, le=127)
    duration: float = Field(gt=0)
    volume: int = Field(ge=0, le=127)


class InstrumentOutputEvent(BaseModel):
    note_id: str
    instrument: str
    rendered_at: datetime
    latency_ms: int = Field(ge=0)
    audio_hint: AudioHint
