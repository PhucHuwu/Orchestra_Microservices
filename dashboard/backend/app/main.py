import asyncio
from datetime import UTC, datetime

from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from fastapi import File, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest
from sqlalchemy.orm import Session

from app.api import ApiError, api_error_handler, success_response, validation_error_handler
from app.audio_renderer import PlaybackAudioRenderer
from app.config import settings
from app.db.session import get_db_session
from app.logging_config import configure_logging
from app.metrics import RabbitMQManagementClient
from app.rabbitmq_client import RabbitMQPublisher, RabbitMQPublisherProvider
from app.schemas import (
    PlaybackStartRequest,
    PlaybackStopRequest,
    ServiceToggleRequest,
    TempoUpdateRequest,
)
from app.services import DashboardService

app = FastAPI(title="Dashboard API", version="0.1.0")
app.add_exception_handler(ApiError, api_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_allow_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
audio_renderer = PlaybackAudioRenderer(
    sample_rate=settings.audio_sample_rate,
    output_dir=settings.audio_output_dir,
    soundfont_path=settings.soundfont_path,
    rabbitmq_url=settings.rabbitmq_url,
    exchange_name=settings.exchange_name,
    output_queue="playback.output",
)
dashboard_service = DashboardService(
    settings=settings,
    publisher=publisher_provider.get(),
    metrics_client=metrics_client,
    audio_renderer=audio_renderer,
)


@app.on_event("startup")
async def on_startup() -> None:
    configure_logging()
    audio_renderer.start()
    await dashboard_service.start_background_tasks()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    audio_renderer.stop()
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


@app.get("/api/v1/scores")
def list_scores(db: Session = Depends(get_db_session)) -> dict:
    _track("/api/v1/scores", "GET")
    scores = dashboard_service.list_scores(db)
    return success_response(scores)


@app.post("/api/v1/scores/upload")
async def upload_score(file: UploadFile = File(...), db: Session = Depends(get_db_session)) -> dict:
    _track("/api/v1/scores/upload", "POST")
    content = await file.read()
    if not content:
        raise ApiError(
            error_code="EMPTY_SCORE_FILE",
            message="Uploaded file is empty",
            status_code=400,
        )
    if file.filename is None:
        raise ApiError(
            error_code="INVALID_SCORE_FILE",
            message="File name is required",
            status_code=400,
        )
    created = dashboard_service.save_uploaded_score(db=db, filename=file.filename, content=content)
    return success_response(created)


@app.get("/api/v1/playback/audio/latest")
def latest_audio() -> Response:
    _track("/api/v1/playback/audio/latest", "GET")
    audio_file = audio_renderer.latest_file_path
    if not audio_file.exists():
        raise ApiError(
            error_code="AUDIO_NOT_READY",
            message="Audio is not generated yet",
            status_code=404,
        )
    return Response(
        content=audio_file.read_bytes(),
        media_type="audio/wav",
        headers={"Accept-Ranges": "bytes"},
    )


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


@app.get("/api/v1/services/control")
async def services_control() -> dict:
    _track("/api/v1/services/control", "GET")
    items = await dashboard_service.service_control_status()
    return success_response([item.model_dump(mode="json") for item in items])


@app.post("/api/v1/services/control")
async def set_service_control(request: ServiceToggleRequest, db: Session = Depends(get_db_session)) -> dict:
    _track("/api/v1/services/control", "POST")
    item = await dashboard_service.set_service_enabled(
        db=db,
        service_name=request.service_name,
        enabled=request.enabled,
    )
    return success_response(item.model_dump(mode="json"))


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
        try:
            await websocket.send_json(
                {
                    "success": False,
                    "error_code": "WS_STREAM_ERROR",
                    "message": "WebSocket stream interrupted",
                    "data": {"ts": datetime.now(UTC).isoformat()},
                }
            )
        except Exception:
            pass
        try:
            await websocket.close()
        except Exception:
            pass
