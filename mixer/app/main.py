from fastapi import FastAPI, Response

from app.config import settings
from app.logging_config import configure_logging
from app.metrics import metrics_payload
from app.worker import MixerWorker

app = FastAPI(title="Mixer Service", version="0.1.0")
worker = MixerWorker(settings=settings)


@app.on_event("startup")
def on_startup() -> None:
    configure_logging()
    worker.start()


@app.on_event("shutdown")
def on_shutdown() -> None:
    worker.stop()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.service_name}


@app.get("/metrics")
def metrics() -> Response:
    payload, content_type = metrics_payload()
    return Response(content=payload, media_type=content_type)
