from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from app.models import (
    ConductorEnabledRequest,
    ConductorEnabledStatus,
    ConductorStartRequest,
    ConductorStatus,
    ConductorStopRequest,
    ConductorTempoRequest,
    ServiceToggleRequest,
    ServiceToggleStatus,
    TempoCommand,
)
from app.service import ConductorRuntime
from app.system_logs import recent_logs

router = APIRouter()
runtime: ConductorRuntime | None = None


def set_runtime(value: ConductorRuntime) -> None:
    global runtime
    runtime = value


def _runtime() -> ConductorRuntime:
    if runtime is None:
        raise HTTPException(status_code=503, detail="Conductor runtime unavailable")
    return runtime


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "conductor"}


@router.post("/v1/conductor/start", response_model=ConductorStatus)
def start(payload: ConductorStartRequest) -> ConductorStatus:
    try:
        return _runtime().start(payload)
    except RuntimeError as exc:
        if str(exc) == "conductor_disabled":
            raise HTTPException(status_code=409, detail="Conductor is disabled") from exc
        raise


@router.post("/v1/conductor/stop", response_model=ConductorStatus)
def stop(payload: ConductorStopRequest) -> ConductorStatus:
    return _runtime().stop(payload.session_id)


@router.post("/v1/conductor/tempo", response_model=ConductorStatus)
def tempo(payload: ConductorTempoRequest) -> ConductorStatus:
    command = TempoCommand(
        session_id=payload.session_id,
        new_bpm=payload.new_bpm,
        issued_by=payload.issued_by,
    )
    return _runtime().set_tempo(command)


@router.get("/v1/conductor/status", response_model=ConductorStatus)
def status() -> ConductorStatus:
    return _runtime().status()


@router.get("/v1/conductor/enabled", response_model=ConductorEnabledStatus)
def enabled_status() -> ConductorEnabledStatus:
    return ConductorEnabledStatus(enabled=_runtime().is_enabled())


@router.post("/v1/conductor/enabled", response_model=ConductorEnabledStatus)
def set_enabled(payload: ConductorEnabledRequest) -> ConductorEnabledStatus:
    enabled = _runtime().set_enabled(payload.enabled)
    return ConductorEnabledStatus(enabled=enabled)


@router.get("/v1/conductor/services")
def services_status() -> dict:
    return {"items": _runtime().service_control_status()}


@router.post("/v1/conductor/services/control", response_model=ServiceToggleStatus)
def services_control(payload: ServiceToggleRequest) -> ServiceToggleStatus:
    try:
        result = _runtime().set_service_enabled(payload.service_name, payload.enabled)
        return ServiceToggleStatus(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Failed to toggle service: {exc}") from exc


@router.get("/v1/conductor/logs")
def system_logs(limit: int = 200) -> dict:
    return {"items": recent_logs(limit)}


@router.get("/ui", response_class=HTMLResponse)
def ui_index() -> str:
    return """
<!doctype html>
<html>
  <head>
    <meta charset='utf-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <title>Conductor Control</title>
    <style>
      body { font-family: Helvetica, sans-serif; margin: 20px; background: #f4f6f8; color: #1a1f2b; }
      .card { background: #fff; border: 1px solid #d9e0e8; border-radius: 10px; padding: 14px; margin-bottom: 12px; }
      button { margin-right: 8px; padding: 6px 10px; border-radius: 8px; border: 1px solid #bcc7d6; background: #fdfefe; cursor: pointer; }
      pre { background: #10151f; color: #d5e2ff; padding: 10px; border-radius: 8px; max-height: 320px; overflow: auto; }
      .row { display: flex; gap: 10px; flex-wrap: wrap; }
    </style>
  </head>
  <body>
    <h2>Conductor Control Panel</h2>
    <div class='card'>
      <h3>Instrument Services</h3>
      <div class='row'>
        <button onclick="toggleService('guitar-service', true)">Start guitar-service</button>
        <button onclick="toggleService('guitar-service', false)">Stop guitar-service</button>
        <button onclick="toggleService('oboe-service', true)">Start oboe-service</button>
        <button onclick="toggleService('oboe-service', false)">Stop oboe-service</button>
        <button onclick="toggleService('drums-service', true)">Start drums-service</button>
        <button onclick="toggleService('drums-service', false)">Stop drums-service</button>
      </div>
      <pre id='services'></pre>
    </div>
    <div class='card'>
      <h3>System Logs</h3>
      <pre id='logs'></pre>
    </div>
    <script>
      async function refresh() {
        const svc = await fetch('/v1/conductor/services').then(r => r.json());
        document.getElementById('services').textContent = JSON.stringify(svc, null, 2);
        const logs = await fetch('/v1/conductor/logs?limit=120').then(r => r.json());
        document.getElementById('logs').textContent = JSON.stringify(logs, null, 2);
      }
      async function toggleService(name, enabled) {
        await fetch('/v1/conductor/services/control', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({service_name: name, enabled})
        });
        await refresh();
      }
      refresh();
      setInterval(refresh, 3000);
    </script>
  </body>
</html>
"""
