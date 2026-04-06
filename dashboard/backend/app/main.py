import asyncio
from datetime import UTC, datetime

from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.exceptions import RequestValidationError
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest
from sqlalchemy.orm import Session

from app.api import ApiError, api_error_handler, success_response, validation_error_handler
from app.config import settings
from app.db.session import get_db_session
from app.logging_config import configure_logging
from app.metrics import RabbitMQManagementClient
from app.rabbitmq_client import RabbitMQPublisher, RabbitMQPublisherProvider
from app.schemas import PlaybackStartRequest, PlaybackStopRequest, TempoUpdateRequest
from app.services import DashboardService

app = FastAPI(title="Dashboard API", version="0.1.0")
app.add_exception_handler(ApiError, api_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)

HTTP_REQUESTS_TOTAL = Counter(
    "dashboard_http_requests_total",
    "Total dashboard API HTTP requests",
    ["path", "method"],
)


def _track(path: str, method: str) -> None:
    HTTP_REQUESTS_TOTAL.labels(path=path, method=method).inc()


publisher_provider = RabbitMQPublisherProvider(
    lambda: RabbitMQPublisher(
        rabbitmq_url=settings.rabbitmq_url,
        exchange_name=settings.exchange_name,
        control_queues=(settings.tempo_control_queue, settings.playback_control_queue),
    )
)
metrics_client = RabbitMQManagementClient(settings)
dashboard_service = DashboardService(
    settings=settings,
    publisher=publisher_provider.get(),
    metrics_client=metrics_client,
)


@app.on_event("startup")
async def on_startup() -> None:
    configure_logging()
    await dashboard_service.start_background_tasks()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await dashboard_service.stop_background_tasks()
    await metrics_client.close()
    publisher_provider.close()


@app.get("/health")
def health() -> dict:
    _track("/health", "GET")
    return {"status": "ok", "service": settings.service_name}


@app.get("/metrics")
def metrics() -> Response:
    _track("/metrics", "GET")
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/api/v1/playback/start")
def start_playback(request: PlaybackStartRequest, db: Session = Depends(get_db_session)) -> dict:
    _track("/api/v1/playback/start", "POST")
    result = dashboard_service.start_playback(
        db=db,
        score_id=request.score_id,
        initial_bpm=request.initial_bpm,
    )
    return success_response(result)


@app.post("/api/v1/playback/stop")
def stop_playback(request: PlaybackStopRequest, db: Session = Depends(get_db_session)) -> dict:
    _track("/api/v1/playback/stop", "POST")
    result = dashboard_service.stop_playback(db=db, session_id=request.session_id)
    return success_response(result)


@app.post("/api/v1/tempo")
def update_tempo(request: TempoUpdateRequest, db: Session = Depends(get_db_session)) -> dict:
    _track("/api/v1/tempo", "POST")
    result = dashboard_service.update_tempo(
        db=db,
        session_id=request.session_id,
        new_bpm=request.new_bpm,
        issued_by=request.issued_by,
    )
    return success_response(result)


@app.get("/api/v1/metrics/overview")
async def metrics_overview() -> dict:
    _track("/api/v1/metrics/overview", "GET")
    overview = await dashboard_service.metrics_overview()
    return success_response(overview)


@app.get("/api/v1/services/health")
async def services_health(db: Session = Depends(get_db_session)) -> dict:
    _track("/api/v1/services/health", "GET")
    health_items = dashboard_service.latest_snapshot_health(db)
    if not health_items:
        health_items = await dashboard_service.services_health()
    return success_response([item.model_dump(mode="json") for item in health_items])


@app.websocket("/ws/metrics")
async def metrics_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    from app.db.session import SessionLocal

    try:
        while True:
            db = SessionLocal()
            try:
                payload = await dashboard_service.ws_metrics_payload(db)
            finally:
                db.close()
            await websocket.send_json(success_response(payload))
            await asyncio.sleep(settings.metrics_stream_interval_seconds)
    except WebSocketDisconnect:
        return
    except Exception:  # noqa: BLE001
        await websocket.send_json(
            {
                "success": False,
                "error_code": "WS_STREAM_ERROR",
                "message": "WebSocket stream interrupted",
                "data": {"ts": datetime.now(UTC).isoformat()},
            }
        )
        await websocket.close()
