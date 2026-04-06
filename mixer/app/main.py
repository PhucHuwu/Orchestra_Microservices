from fastapi import FastAPI, Response

from app.config import settings
from app.logging_config import configure_logging
from app.metrics import metrics_payload
from app.worker import MixerWorker

app = FastAPI(title="Mixer Service", version="0.1.0")
worker = MixerWorker(settings=settings)
worker_enabled = True


@app.on_event("startup")
def on_startup() -> None:
    configure_logging()
    if worker_enabled:
        worker.start()


@app.on_event("shutdown")
def on_shutdown() -> None:
    worker.stop()


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "service": settings.service_name,
        "worker_enabled": worker_enabled,
        "worker_running": worker.is_running(),
    }


@app.get("/control/worker")
def worker_control_status() -> dict[str, bool]:
    return {"enabled": worker_enabled, "running": worker.is_running()}


@app.post("/control/worker/start")
def worker_control_start() -> dict[str, bool]:
    global worker_enabled
    worker_enabled = True
    worker.start()
    return {"enabled": worker_enabled, "running": worker.is_running()}


@app.post("/control/worker/stop")
def worker_control_stop() -> dict[str, bool]:
    global worker_enabled
    worker_enabled = False
    worker.stop()
    return {"enabled": worker_enabled, "running": worker.is_running()}


@app.get("/metrics")
def metrics() -> Response:
    payload, content_type = metrics_payload()
    return Response(content=payload, media_type=content_type)
