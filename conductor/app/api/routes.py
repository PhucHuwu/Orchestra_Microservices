from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "conductor"}


@router.post("/v1/conductor/start")
def start() -> dict:
    return {"accepted": True, "status": "running"}


@router.post("/v1/conductor/stop")
def stop() -> dict:
    return {"accepted": True, "status": "stopped"}


@router.post("/v1/conductor/tempo")
def tempo() -> dict:
    return {"accepted": True}


@router.get("/v1/conductor/status")
def status() -> dict:
    return {"status": "idle"}
