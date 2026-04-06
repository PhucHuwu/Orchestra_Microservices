from __future__ import annotations

from fastapi import APIRouter, Response
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, generate_latest


def build_metrics_router(registry: CollectorRegistry | None = None) -> APIRouter:
    router = APIRouter()

    @router.get("/metrics")
    def metrics() -> Response:
        payload = generate_latest(registry)
        return Response(content=payload, media_type=CONTENT_TYPE_LATEST)

    return router
