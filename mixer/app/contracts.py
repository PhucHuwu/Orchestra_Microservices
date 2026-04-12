from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AudioHint(BaseModel):
    pitch: int = Field(ge=0, le=127)
    duration: float = Field(gt=0)
    volume: int = Field(ge=0, le=127)


class InstrumentOutputEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")

    note_id: UUID
    instrument: Literal["guitar", "oboe", "drums", "bass"]
    beat_time: float = Field(ge=0)
    rendered_at: datetime
    latency_ms: int = Field(ge=0)
    audio_hint: AudioHint


class PlaybackEvent(BaseModel):
    playback_id: UUID
    note_id: UUID
    instrument: Literal["guitar", "oboe", "drums", "bass"]
    pitch: int = Field(ge=0, le=127)
    duration: float = Field(gt=0)
    volume: int = Field(ge=0, le=127)
    scheduled_beat_time: float
    emitted_at: datetime

