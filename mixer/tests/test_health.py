from app.main import app
from fastapi.testclient import TestClient


def test_health() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "mixer"


def test_metrics_endpoint_exposed() -> None:
    client = TestClient(app)
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
