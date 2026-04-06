from fastapi import APIRouter, HTTPException

from app.models import (
    ConductorEnabledRequest,
    ConductorEnabledStatus,
    ConductorStartRequest,
    ConductorStatus,
    ConductorStopRequest,
    ConductorTempoRequest,
    TempoCommand,
)
from app.service import ConductorRuntime

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
