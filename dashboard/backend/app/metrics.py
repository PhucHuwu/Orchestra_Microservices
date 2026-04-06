from __future__ import annotations

import time
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx

from app.config import Settings


@dataclass
class QueueStats:
    queue_depth: int
    consumer_count: int
    message_rate: float


class RabbitMQManagementClient:
    def __init__(self, settings: Settings) -> None:
        self._base_url = settings.rabbitmq_mgmt_api_url.rstrip("/")
        self._timeout = settings.rabbitmq_timeout_seconds
        username, password = _resolve_management_auth(settings)
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=self._timeout,
            auth=(username, password),
        )

    async def fetch_queues(self) -> tuple[list[dict], float]:
        started = time.perf_counter()
        response = await self._client.get("/queues")
        response.raise_for_status()
        elapsed_ms = (time.perf_counter() - started) * 1000
        return response.json(), elapsed_ms

    async def close(self) -> None:
        await self._client.aclose()


def _resolve_management_auth(settings: Settings) -> tuple[str, str]:
    if settings.rabbitmq_mgmt_username and settings.rabbitmq_mgmt_password:
        return settings.rabbitmq_mgmt_username, settings.rabbitmq_mgmt_password

    parsed = urlparse(settings.rabbitmq_url)
    username = parsed.username or "guest"
    password = parsed.password or "guest"
    return username, password


def parse_queue_stats(queue_payload: dict) -> QueueStats:
    message_stats = queue_payload.get("message_stats") or {}
    rate = 0.0
    for key in ("publish_details", "deliver_get_details"):
        details = message_stats.get(key) or {}
        if isinstance(details.get("rate"), (int, float)):
            rate = max(rate, float(details["rate"]))

    return QueueStats(
        queue_depth=int(queue_payload.get("messages") or 0),
        consumer_count=int(queue_payload.get("consumers") or 0),
        message_rate=rate,
    )
