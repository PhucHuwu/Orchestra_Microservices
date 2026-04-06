from fastapi.testclient import TestClient

from app.main import app, dashboard_service


def test_ws_metrics_stream_sends_envelope(monkeypatch) -> None:
    async def fake_ws_payload(db):
        return {
            "ts": "2026-04-06T10:10:00+00:00",
            "metrics": {
                "queue_depth": {"playback.output": 2},
                "consumer_count": {"playback.output": 1},
                "message_rate": {"playback.output": 5.0},
                "health_summary": {"healthy_services": 1, "degraded_services": 0},
                "services": [],
            },
        }

    monkeypatch.setattr(dashboard_service, "ws_metrics_payload", fake_ws_payload)
    client = TestClient(app)
    with client.websocket_connect("/ws/metrics") as websocket:
        payload = websocket.receive_json()

    assert payload["success"] is True
    assert payload["data"]["metrics"]["queue_depth"]["playback.output"] == 2
