from fastapi import FastAPI

from app.api.routes import router, set_runtime
from app.config import settings
from app.logging_config import configure_logging
from app.service import ConductorRuntime

app = FastAPI(title="Conductor Service", version="0.1.0")
app.include_router(router)


@app.on_event("startup")
def on_startup() -> None:
    configure_logging()
    set_runtime(ConductorRuntime(settings))
