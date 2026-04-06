from __future__ import annotations

import logging
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Iterator

from pythonjsonlogger import jsonlogger

_LOG_CONTEXT: ContextVar[dict[str, Any]] = ContextVar("orchestra_log_context", default={})


class ContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        context = _LOG_CONTEXT.get()
        for key, value in context.items():
            setattr(record, key, value)
        return True


def configure_structured_logging(service_name: str) -> None:
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return

    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s "
        "%(service_name)s %(event)s %(message_id)s %(session_id)s %(latency_ms)s"
    )
    handler.setFormatter(formatter)
    handler.addFilter(ContextFilter())

    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

    _LOG_CONTEXT.set(
        {
            "service_name": service_name,
            "event": "",
            "message_id": "",
            "session_id": "",
            "latency_ms": 0,
        }
    )


@contextmanager
def log_context(**kwargs: Any) -> Iterator[None]:
    current = dict(_LOG_CONTEXT.get())
    current.update(kwargs)
    token = _LOG_CONTEXT.set(current)
    try:
        yield
    finally:
        _LOG_CONTEXT.reset(token)
