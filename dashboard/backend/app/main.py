from datetime import datetime, timezone

from fastapi import FastAPI, WebSocket
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest

app = FastAPI(title="Dashboard API", version="0.1.0")

HTTP_REQUESTS_TOTAL = Counter(
    "dashboard_http_requests_total",
    "Total dashboard API HTTP requests",
    ["path", "method"],
)


def _track(path: str, method: str) -> None:
    HTTP_REQUESTS_TOTAL.labels(path=path, method=method).inc()


@app.get("/health")
def health() -> dict:
    _track("/health", "GET")
    return {"status": "ok", "service": "dashboard-api"}


@app.get("/metrics")
def metrics() -> Response:
    _track("/metrics", "GET")
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/api/v1/playback/start")
def start_playback() -> dict:
    _track("/api/v1/playback/start", "POST")
    return {"success": True, "data": {"session_id": "TODO", "status": "running"}}


@app.post("/api/v1/playback/stop")
def stop_playback() -> dict:
    _track("/api/v1/playback/stop", "POST")
    return {"success": True, "data": {"status": "stopped"}}


@app.post("/api/v1/tempo")
def update_tempo() -> dict:
    _track("/api/v1/tempo", "POST")
    return {"success": True, "data": {"status": "accepted"}}


@app.get("/api/v1/metrics/overview")
def metrics_overview() -> dict:
    _track("/api/v1/metrics/overview", "GET")
    return {"success": True, "data": {"queue_depth": {}, "message_rate": {}}}


@app.get("/api/v1/services/health")
def services_health() -> dict:
    _track("/api/v1/services/health", "GET")
    return {"success": True, "data": []}


@app.websocket("/ws/metrics")
async def metrics_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    payload = {
        "success": True,
        "data": {
            "ts": datetime.now(tz=timezone.utc).isoformat(),
            "metrics": {},
        },
    }
    await websocket.send_json(payload)
    await websocket.close()
