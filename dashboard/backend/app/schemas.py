from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PlaybackStartRequest(BaseModel):
    score_id: UUID
    initial_bpm: int = Field(ge=20, le=300)


class PlaybackStopRequest(BaseModel):
    session_id: UUID


class TempoUpdateRequest(BaseModel):
    session_id: UUID
    new_bpm: int = Field(ge=20, le=300)
    issued_by: str = Field(default="dashboard", min_length=1, max_length=80)


class MetricsOverview(BaseModel):
    model_config = ConfigDict(extra="ignore")

    queue_depth: dict[str, int]
    consumer_count: dict[str, int]
    message_rate: dict[str, float]
    health_summary: dict[str, int]


class ServiceHealthItem(BaseModel):
    service_name: str
    status: str
    latency_ms: int | None = None
    queue_depth: int = 0
    consumer_count: int = 0
    captured_at: datetime | None = None
