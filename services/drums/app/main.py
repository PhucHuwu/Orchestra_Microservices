from __future__ import annotations

import os
from contextlib import asynccontextmanager
from threading import Lock
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
    SERVICE_NAME=os.getenv("SERVICE_NAME", "drums-service"),
    INSTRUMENT_NAME=os.getenv("INSTRUMENT_NAME", "drums"),
    INPUT_QUEUE=os.getenv("INPUT_QUEUE", "instrument.drums.beat"),
    OUTPUT_ROUTING_KEY=os.getenv(
        "OUTPUT_ROUTING_KEY",
        default_output_routing_key(os.getenv("INSTRUMENT_NAME", "drums")),
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
worker_lock = Lock()


def _worker_running() -> bool:
    return worker_thread is not None and worker_thread.is_alive()


def _start_worker_unlocked() -> None:
    global worker_thread
    if _worker_running():
        return
    if not worker_enabled:
        return
    worker._running = True
    worker_thread = Thread(target=worker.start, daemon=True)
    worker_thread.start()


def _stop_worker_unlocked() -> None:
    global worker_thread
    if not _worker_running():
        worker_thread = None
        return
    worker.stop()
    if worker_thread is not None:
        worker_thread.join(timeout=2.0)
    worker_thread = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    if worker_enabled:
        with worker_lock:
            _start_worker_unlocked()
    yield
    with worker_lock:
        _stop_worker_unlocked()


app = FastAPI(title="Drums Service", version="0.1.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": settings.service_name,
        "instrument": settings.instrument_name,
        "input_queue": settings.input_queue,
        "output_routing_key": settings.output_routing_key,
        "worker_enabled": worker_enabled,
        "worker_running": _worker_running(),
        "metrics": worker.metrics_snapshot(),
    }


@app.get("/control/worker")
def worker_control_status() -> dict:
    return {
        "enabled": worker_enabled,
        "running": _worker_running(),
    }


@app.post("/control/worker/start")
def worker_control_start() -> dict:
    global worker_enabled
    with worker_lock:
        worker_enabled = True
        _start_worker_unlocked()
        return {
            "enabled": worker_enabled,
            "running": _worker_running(),
        }


@app.post("/control/worker/stop")
def worker_control_stop() -> dict:
    global worker_enabled
    with worker_lock:
        worker_enabled = False
        _stop_worker_unlocked()
        return {
            "enabled": worker_enabled,
            "running": _worker_running(),
        }
