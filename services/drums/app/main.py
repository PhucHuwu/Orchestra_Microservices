from __future__ import annotations

import os
from contextlib import asynccontextmanager
from threading import Lock
from threading import Thread
from typing import Any

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from services.instruments_shared import (
    InstrumentSettings,
    InstrumentWorker,
    default_output_routing_key,
)
from services.instruments_shared.logging_config import configure_logging

configure_logging()

primary_settings = InstrumentSettings(
    SERVICE_NAME=os.getenv("SERVICE_NAME", "drums-service"),
    INSTRUMENT_NAME=os.getenv("INSTRUMENT_NAME", "drums"),
    INPUT_QUEUE=os.getenv("INPUT_QUEUE", "instrument.drums.beat"),
    OUTPUT_ROUTING_KEY=os.getenv(
        "OUTPUT_ROUTING_KEY",
        default_output_routing_key(os.getenv("INSTRUMENT_NAME", "drums")),
    ),
)

secondary_settings = InstrumentSettings(
    SERVICE_NAME=os.getenv("SERVICE_NAME", "drums-service"),
    INSTRUMENT_NAME=os.getenv("SECONDARY_INSTRUMENT_NAME", "bass"),
    INPUT_QUEUE=os.getenv("SECONDARY_INPUT_QUEUE", "instrument.bass.note"),
    OUTPUT_ROUTING_KEY=os.getenv(
        "SECONDARY_OUTPUT_ROUTING_KEY",
        default_output_routing_key(os.getenv("SECONDARY_INSTRUMENT_NAME", "bass")),
    ),
)

workers = {
    primary_settings.instrument_name: InstrumentWorker(primary_settings),
    secondary_settings.instrument_name: InstrumentWorker(secondary_settings),
}
worker_threads: dict[str, Thread | None] = {
    instrument: None for instrument in workers
}

worker_enabled = os.getenv("INSTRUMENT_WORKER_ENABLED", "false").lower() in {
    "1",
    "true",
    "yes",
    "on",
}
worker_lock = Lock()


def _worker_running(instrument: str) -> bool:
    thread = worker_threads.get(instrument)
    return thread is not None and thread.is_alive()


def _running_status() -> dict[str, bool]:
    return {instrument: _worker_running(instrument) for instrument in workers}


def _any_worker_running() -> bool:
    return any(_running_status().values())


def _start_worker_unlocked() -> None:
    for instrument, worker in workers.items():
        if _worker_running(instrument):
            continue
        thread = Thread(target=worker.start, daemon=True)
        thread.start()
        worker_threads[instrument] = thread


def _stop_worker_unlocked() -> None:
    for instrument, worker in workers.items():
        if _worker_running(instrument):
            worker.stop()

    for instrument in workers:
        thread = worker_threads.get(instrument)
        if thread is not None:
            thread.join(timeout=2.0)
        worker_threads[instrument] = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    if worker_enabled:
        with worker_lock:
            _start_worker_unlocked()
    yield
    with worker_lock:
        _stop_worker_unlocked()


app = FastAPI(title="Auxiliary Instruments Service", version="0.1.0", lifespan=lifespan)


def _worker_details() -> dict[str, dict[str, Any]]:
    details: dict[str, dict[str, Any]] = {}
    for instrument, worker in workers.items():
        details[instrument] = {
            "running": _worker_running(instrument),
            "metrics": worker.metrics_snapshot(),
        }
    return details


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": primary_settings.service_name,
        "instruments": list(workers.keys()),
        "worker_enabled": worker_enabled,
        "worker_running": _any_worker_running(),
        "workers": _worker_details(),
    }


@app.get("/control/worker")
def worker_control_status() -> dict:
    return {
        "enabled": worker_enabled,
        "running": _any_worker_running(),
        "workers": _running_status(),
    }


@app.post("/control/worker/start")
def worker_control_start() -> dict:
    global worker_enabled
    with worker_lock:
        worker_enabled = True
        _start_worker_unlocked()
        return {
            "enabled": worker_enabled,
            "running": _any_worker_running(),
            "workers": _running_status(),
        }


@app.post("/control/worker/stop")
def worker_control_stop() -> dict:
    global worker_enabled
    with worker_lock:
        worker_enabled = False
        _stop_worker_unlocked()
        return {
            "enabled": worker_enabled,
            "running": _any_worker_running(),
            "workers": _running_status(),
        }


@app.get("/ui", response_class=HTMLResponse)
def ui() -> str:
    return """
<!doctype html>
<html>
  <head>
    <meta charset='utf-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <title>Aux Service Control</title>
  </head>
  <body style='font-family: Arial, sans-serif; margin: 20px;'>
    <h3>Aux Instruments Service (drums + bass)</h3>
    <button onclick='toggle(true)'>Start</button>
    <button onclick='toggle(false)'>Stop</button>
    <pre id='out'></pre>
    <script>
      async function refresh(){
        const data = await fetch('/control/worker').then(r=>r.json());
        document.getElementById('out').textContent = JSON.stringify(data, null, 2);
      }
      async function toggle(enabled){
        const path = enabled ? '/control/worker/start' : '/control/worker/stop';
        await fetch(path, {method:'POST'});
        await refresh();
      }
      refresh();
      setInterval(refresh, 3000);
    </script>
  </body>
</html>
"""
