from __future__ import annotations

import httpx
import pytest

from app.config import Settings
from app.services import DashboardService


class DummyPublisher:
    def publish_json(self, routing_key: str, payload: dict) -> None:  # noqa: ARG002
        return


class DummyMetricsClient:
    def __init__(self) -> None:
        self.calls = 0

    async def fetch_queues(self):
        self.calls += 1
        return (
            [
                {
                    "name": "tempo.control",
                    "messages": 3,
                    "consumers": 1,
                    "message_stats": {"publish_details": {"rate": 12.5}},
                }
            ],
            12.3,
        )


class TimeoutThenSuccessClient:
    def __init__(self) -> None:
        self.calls = 0

    async def fetch_queues(self):
        self.calls += 1
        if self.calls == 1:
            raise httpx.TimeoutException("timeout")
        return (
            [
                {
                    "name": "playback.output",
                    "messages": 0,
                    "consumers": 0,
                    "message_stats": {},
                }
            ],
            5.0,
        )


@pytest.mark.asyncio
async def test_metrics_overview_maps_queue_stats() -> None:
    settings = Settings()
    service = DashboardService(settings, DummyPublisher(), DummyMetricsClient())

    payload = await service.metrics_overview()
    assert payload["queue_depth"]["tempo.control"] == 3
    assert payload["consumer_count"]["tempo.control"] == 1
    assert payload["message_rate"]["tempo.control"] == 12.5
    assert payload["health_summary"] == {"healthy_services": 1, "degraded_services": 0}


@pytest.mark.asyncio
async def test_metrics_overview_retries_on_timeout() -> None:
    settings = Settings()
    client = TimeoutThenSuccessClient()
    service = DashboardService(settings, DummyPublisher(), client)

    payload = await service.metrics_overview()
    assert client.calls == 2
    assert payload["queue_depth"]["playback.output"] == 0
