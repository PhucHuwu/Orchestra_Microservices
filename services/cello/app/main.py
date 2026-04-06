from __future__ import annotations

import os
from contextlib import asynccontextmanager
from threading import Thread

from fastapi import FastAPI

from services.instruments_shared import (
    InstrumentSettings,
    InstrumentWorker,
    default_output_routing_key,
)
from services.instruments_shared.logging_config import configure_logging

configure_logging()

settings = InstrumentSettings(
    SERVICE_NAME=os.getenv("SERVICE_NAME", "cello-service"),
    INSTRUMENT_NAME=os.getenv("INSTRUMENT_NAME", "cello"),
    INPUT_QUEUE=os.getenv("INPUT_QUEUE", "instrument.cello.note"),
    OUTPUT_ROUTING_KEY=os.getenv(
        "OUTPUT_ROUTING_KEY",
        default_output_routing_key(os.getenv("INSTRUMENT_NAME", "cello")),
    ),
)
worker = InstrumentWorker(settings)
worker_thread: Thread | None = None
worker_enabled = os.getenv("INSTRUMENT_WORKER_ENABLED", "false").lower() in {
    "1",
    "true",
    "yes",
    "on",
}


@asynccontextmanager
async def lifespan(_: FastAPI):
    global worker_thread
    if worker_enabled:
        worker_thread = Thread(target=worker.start, daemon=True)
        worker_thread.start()
    yield
    if worker_enabled:
        worker.stop()


app = FastAPI(title="Cello Service", version="0.1.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": settings.service_name,
        "instrument": settings.instrument_name,
        "input_queue": settings.input_queue,
        "output_routing_key": settings.output_routing_key,
        "worker_enabled": worker_enabled,
        "metrics": worker.metrics_snapshot(),
    }
