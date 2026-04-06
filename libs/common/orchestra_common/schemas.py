from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from pydantic import BaseModel, Field


class BaseEvent(BaseModel):
    message_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
