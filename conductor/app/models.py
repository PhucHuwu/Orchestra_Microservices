from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


INSTRUMENTS = ("guitar", "oboe", "drums", "bass")


class ParsedNote(BaseModel):
    instrument: Literal["guitar", "oboe", "drums", "bass"]
    pitch: int = Field(ge=0, le=127)
    duration: float = Field(gt=0)
    volume: int = Field(ge=0, le=127)
    beat_position: float = Field(ge=0)


class NoteEvent(BaseModel):
    note_id: UUID = Field(default_factory=uuid4)
    session_id: UUID
    instrument: Literal["guitar", "oboe", "drums", "bass"]
    pitch: int = Field(ge=0, le=127)
    duration: float = Field(gt=0)
    volume: int = Field(ge=0, le=127)
    beat_time: float = Field(ge=0)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TempoCommand(BaseModel):
    session_id: UUID
    new_bpm: int = Field(ge=30, le=300)
    issued_by: str = Field(default="dashboard", min_length=1, max_length=80)
    issued_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ConductorStartRequest(BaseModel):
    score_path: str
    initial_bpm: int = Field(ge=30, le=300)
    session_id: UUID = Field(default_factory=uuid4)


class ConductorStopRequest(BaseModel):
    session_id: UUID


class ConductorTempoRequest(BaseModel):
    session_id: UUID
    new_bpm: int = Field(ge=30, le=300)
    issued_by: str = Field(default="dashboard", min_length=1, max_length=80)


class ConductorEnabledRequest(BaseModel):
    enabled: bool


class ConductorEnabledStatus(BaseModel):
    enabled: bool


class ConductorStatus(BaseModel):
    status: Literal["running", "stopped", "failed"] = "stopped"
    session_id: UUID | None = None
    bpm: int | None = None
    published_notes: int = 0
    total_notes: int = 0
    last_error: str | None = None


def routing_key_for_instrument(instrument: str) -> str:
    mapping = {
        "guitar": "instrument.guitar.note",
        "oboe": "instrument.oboe.note",
        "drums": "instrument.drums.beat",
        "bass": "instrument.bass.note",
    }
    if instrument not in mapping:
        raise ValueError(f"Unsupported instrument: {instrument}")
    return mapping[instrument]


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

