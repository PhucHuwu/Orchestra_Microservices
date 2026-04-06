from fastapi.testclient import TestClient

from app.main import app, dashboard_service


def test_metrics_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]


def test_services_health_endpoint_success_envelope(monkeypatch) -> None:
    async def fake_service_health():
        return []

    def fake_latest_snapshot_health(_db):
        return []

    monkeypatch.setattr(dashboard_service, "services_health", fake_service_health)
    monkeypatch.setattr(dashboard_service, "latest_snapshot_health", fake_latest_snapshot_health)
    client = TestClient(app)
    response = client.get("/api/v1/services/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
