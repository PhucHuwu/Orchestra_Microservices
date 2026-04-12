from __future__ import annotations

import logging
from collections import deque
from datetime import UTC, datetime
from threading import Lock
from typing import Any

_LOGS: deque[dict[str, Any]] = deque(maxlen=500)
_LOCK = Lock()


class InMemoryLogHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        payload = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        with _LOCK:
            _LOGS.append(payload)


def recent_logs(limit: int = 200) -> list[dict[str, Any]]:
    capped = max(1, min(500, int(limit)))
    with _LOCK:
        return list(_LOGS)[-capped:]
