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


class ServiceToggleRequest(BaseModel):
    service_name: str = Field(min_length=1, max_length=80)
    enabled: bool


class ServiceToggleItem(BaseModel):
    service_name: str
    enabled: bool
    reachable: bool
    worker_enabled: bool | None = None
    status: str
    message: str | None = None


class InteractionEdge(BaseModel):
    from_service: str
    to_service: str
    queue: str
    depth: int
    consumers: int
    message_rate: float


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
