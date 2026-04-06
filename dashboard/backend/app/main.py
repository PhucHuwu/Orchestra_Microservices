from datetime import datetime, timezone

from fastapi import FastAPI, WebSocket

app = FastAPI(title="Dashboard API", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "dashboard-api"}


@app.post("/api/v1/playback/start")
def start_playback() -> dict:
    return {"success": True, "data": {"session_id": "TODO", "status": "running"}}


@app.post("/api/v1/playback/stop")
def stop_playback() -> dict:
    return {"success": True, "data": {"status": "stopped"}}


@app.post("/api/v1/tempo")
def update_tempo() -> dict:
    return {"success": True, "data": {"status": "accepted"}}


@app.get("/api/v1/metrics/overview")
def metrics_overview() -> dict:
    return {"success": True, "data": {"queue_depth": {}, "message_rate": {}}}


@app.get("/api/v1/services/health")
def services_health() -> dict:
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
