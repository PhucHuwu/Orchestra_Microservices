from uuid import uuid4

from fastapi.testclient import TestClient

from app.api import ApiError
from app.db.session import get_db_session
from app.main import app, dashboard_service


def _override_db_session():
    yield object()


def test_playback_start_success_envelope(monkeypatch) -> None:
    session_id = str(uuid4())

    def fake_start_playback(db, score_id, initial_bpm):
        return {"session_id": session_id, "status": "running"}

    monkeypatch.setattr(dashboard_service, "start_playback", fake_start_playback)
    app.dependency_overrides[get_db_session] = _override_db_session
    try:
        client = TestClient(app)
        response = client.post(
            "/api/v1/playback/start",
            json={"score_id": str(uuid4()), "initial_bpm": 120},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload == {"success": True, "data": {"session_id": session_id, "status": "running"}}


def test_playback_start_error_envelope(monkeypatch) -> None:
    def fake_start_playback(db, score_id, initial_bpm):
        raise ApiError("SCORE_NOT_FOUND", "Score not found", 404)

    monkeypatch.setattr(dashboard_service, "start_playback", fake_start_playback)
    app.dependency_overrides[get_db_session] = _override_db_session
    try:
        client = TestClient(app)
        response = client.post(
            "/api/v1/playback/start",
            json={"score_id": str(uuid4()), "initial_bpm": 120},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json() == {
        "success": False,
        "error_code": "SCORE_NOT_FOUND",
        "message": "Score not found",
    }


def test_tempo_validation_error_envelope() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/tempo",
        json={"session_id": str(uuid4()), "new_bpm": 10},
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["success"] is False
    assert payload["error_code"] == "VALIDATION_ERROR"


def test_metrics_overview_envelope(monkeypatch) -> None:
    async def fake_metrics_overview():
        return {
            "queue_depth": {"tempo.control": 0},
            "consumer_count": {"tempo.control": 1},
            "message_rate": {"tempo.control": 0.0},
            "health_summary": {"healthy_services": 1, "degraded_services": 0},
        }

    monkeypatch.setattr(dashboard_service, "metrics_overview", fake_metrics_overview)
    client = TestClient(app)
    response = client.get("/api/v1/metrics/overview")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["queue_depth"]["tempo.control"] == 0
