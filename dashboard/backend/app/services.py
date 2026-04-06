from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from datetime import UTC, datetime
from uuid import UUID
from uuid import uuid4

import httpx
import pika
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api import ApiError
from app.audio_renderer import PlaybackAudioRenderer
from app.config import Settings
from app.db.models import PlaybackSession, Score, ServiceHealthSnapshot, TempoCommandAudit
from app.metrics import RabbitMQManagementClient, parse_queue_stats
from app.rabbitmq_client import RabbitMQPublisher
from app.schemas import InteractionEdge, ServiceHealthItem, ServiceToggleItem

LOGGER = logging.getLogger(__name__)

SERVICE_ENDPOINTS = {
    "violin-service": {"url_attr": "violin_service_url", "toggle_path": "/control/worker", "health_path": "/health"},
    "piano-service": {"url_attr": "piano_service_url", "toggle_path": "/control/worker", "health_path": "/health"},
    "drums-service": {"url_attr": "drums_service_url", "toggle_path": "/control/worker", "health_path": "/health"},
    "cello-service": {"url_attr": "cello_service_url", "toggle_path": "/control/worker", "health_path": "/health"},
    "mixer": {"url_attr": "mixer_service_url", "toggle_path": "/control/worker", "health_path": "/health"},
    "conductor": {"url_attr": "conductor_service_url", "toggle_path": "/v1/conductor/enabled", "health_path": "/health"},
}

SERVICE_TO_INSTRUMENT = {
    "violin-service": "violin",
    "piano-service": "piano",
    "drums-service": "drums",
    "cello-service": "cello",
}

INSTRUMENT_INPUT_QUEUE = {
    "violin": "instrument.violin.note",
    "piano": "instrument.piano.note",
    "drums": "instrument.drums.beat",
    "cello": "instrument.cello.note",
}

SERVICE_CONTROL_ORDER = (
    "conductor",
    "violin-service",
    "piano-service",
    "drums-service",
    "cello-service",
    "mixer",
)

QUEUE_FLOW_EDGES = [
    ("conductor", "violin-service", "instrument.violin.note"),
    ("conductor", "piano-service", "instrument.piano.note"),
    ("conductor", "drums-service", "instrument.drums.beat"),
    ("conductor", "cello-service", "instrument.cello.note"),
    ("violin-service", "mixer", "instrument.output"),
    ("piano-service", "mixer", "instrument.output"),
    ("drums-service", "mixer", "instrument.output"),
    ("cello-service", "mixer", "instrument.output"),
    ("mixer", "dashboard-api", "playback.output"),
]


class DashboardService:
    def __init__(
        self,
        settings: Settings,
        publisher: RabbitMQPublisher,
        metrics_client: RabbitMQManagementClient,
        audio_renderer: PlaybackAudioRenderer,
    ) -> None:
        self._settings = settings
        self._publisher = publisher
        self._metrics_client = metrics_client
        self._audio_renderer = audio_renderer
        self._snapshot_task: asyncio.Task[None] | None = None
        self._snapshot_stop = asyncio.Event()
        self._scores_dir = Path(self._settings.score_storage_dir).resolve()
        self._scores_dir.mkdir(parents=True, exist_ok=True)

    async def start_background_tasks(self) -> None:
        if self._snapshot_task is not None:
            return
        self._snapshot_stop.clear()
        self._snapshot_task = asyncio.create_task(self._snapshot_loop())

    async def stop_background_tasks(self) -> None:
        self._snapshot_stop.set()
        if self._snapshot_task is not None:
            await self._snapshot_task
            self._snapshot_task = None

    def start_playback(self, db: Session, score_id: UUID, initial_bpm: int) -> dict:
        score = db.get(Score, score_id)
        if score is None:
            raise ApiError(error_code="SCORE_NOT_FOUND", message="Score not found", status_code=404)

        score_file_name = self._score_file_name(score.source_path)
        score_file_path = self._scores_dir / score_file_name
        if not score_file_path.exists():
            raise ApiError(
                error_code="SCORE_FILE_NOT_FOUND",
                message="Score file is missing. Please upload a MIDI file first.",
                status_code=400,
            )

        session = PlaybackSession(
            id=uuid4(),
            score_id=score.id,
            status="running",
            started_at=datetime.now(UTC),
            initial_bpm=initial_bpm,
        )
        db.add(session)
        db.commit()

        try:
            self._audio_renderer.render_midi_file(str(score_file_path), bpm=initial_bpm)

            for instrument in ("violin", "piano", "drums", "cello"):
                self._audio_renderer.set_instrument_enabled(instrument, True)

            self._publisher.publish_json(
                routing_key=self._settings.playback_control_queue,
                payload={
                    "action": "start",
                    "session_id": str(session.id),
                    "score_id": str(score.id),
                    "initial_bpm": initial_bpm,
                    "issued_at": datetime.now(UTC).isoformat(),
                },
            )

            self._call_conductor_start(
                session_id=session.id,
                score_path=score_file_name,
                initial_bpm=initial_bpm,
            )
        except ApiError:
            session.status = "failed"
            db.commit()
            raise
        except Exception as exc:  # noqa: BLE001
            session.status = "failed"
            db.commit()
            LOGGER.exception("audio_render_failed", extra={"score_path": str(score_file_path)})
            raise ApiError(
                error_code="AUDIO_RENDER_FAILED",
                message="Failed to render audio from MIDI",
                status_code=500,
            ) from exc

        return {"session_id": str(session.id), "status": "running"}

    def stop_playback(self, db: Session, session_id: UUID) -> dict:
        session = db.get(PlaybackSession, session_id)
        if session is None:
            raise ApiError(
                error_code="SESSION_NOT_FOUND", message="Session not found", status_code=404
            )

        if session.status != "stopped":
            session.status = "stopped"
            session.ended_at = datetime.now(UTC)
            db.commit()

        self._publisher.publish_json(
            routing_key=self._settings.playback_control_queue,
            payload={
                "action": "stop",
                "session_id": str(session.id),
                "issued_at": datetime.now(UTC).isoformat(),
            },
        )

        self._call_conductor_stop(session.id)

        return {"status": "stopped"}

    def update_tempo(self, db: Session, session_id: UUID, new_bpm: int, issued_by: str) -> dict:
        session = db.get(PlaybackSession, session_id)
        if session is None:
            raise ApiError(
                error_code="SESSION_NOT_FOUND", message="Session not found", status_code=404
            )

        old_bpm = session.initial_bpm
        session.initial_bpm = new_bpm

        audit = TempoCommandAudit(
            id=uuid4(),
            session_id=session.id,
            old_bpm=old_bpm,
            new_bpm=new_bpm,
            issued_by=issued_by,
            issued_at=datetime.now(UTC),
        )
        db.add(audit)
        db.commit()

        self._publisher.publish_json(
            routing_key=self._settings.tempo_control_queue,
            payload={
                "session_id": str(session.id),
                "new_bpm": new_bpm,
                "issued_by": issued_by,
                "issued_at": datetime.now(UTC).isoformat(),
            },
        )

        self._call_conductor_tempo(session.id, new_bpm, issued_by)
        self._audio_renderer.set_tempo(new_bpm)

        return {"status": "accepted"}

    def list_scores(self, db: Session) -> list[dict[str, str]]:
        stmt = select(Score).order_by(Score.created_at.desc())
        scores = db.execute(stmt).scalars().all()
        response: list[dict[str, str]] = []
        for score in scores:
            score_file_name = self._score_file_name(score.source_path)
            if not (self._scores_dir / score_file_name).exists():
                continue
            response.append(
                {
                    "id": str(score.id),
                    "name": score.name,
                    "source_type": score.source_type,
                    "source_path": score.source_path,
                }
            )
        return response

    def save_uploaded_score(self, db: Session, filename: str, content: bytes) -> dict[str, str]:
        safe_name = Path(filename).name
        if not safe_name.lower().endswith(".mid"):
            raise ApiError(
                error_code="INVALID_SCORE_FILE",
                message="Only .mid files are supported",
                status_code=400,
            )

        score_id = uuid4()
        file_name = f"{score_id.hex}.mid"
        file_path = self._scores_dir / file_name
        file_path.write_bytes(content)

        score = Score(
            id=score_id,
            name=Path(safe_name).stem,
            source_type="midi",
            source_path=file_name,
            created_at=datetime.now(UTC),
        )
        db.add(score)
        db.commit()

        return {
            "id": str(score.id),
            "name": score.name,
            "source_type": score.source_type,
            "source_path": score.source_path,
        }

    async def metrics_overview(self) -> dict:
        queues, _ = await self._fetch_queues_with_retry()
        queue_depth: dict[str, int] = {}
        consumer_count: dict[str, int] = {}
        message_rate: dict[str, float] = {}

        for queue in queues:
            name = queue.get("name", "unknown")
            stats = parse_queue_stats(queue)
            queue_depth[name] = stats.queue_depth
            consumer_count[name] = stats.consumer_count
            message_rate[name] = stats.message_rate

        health_summary = {
            "healthy_services": sum(1 for count in consumer_count.values() if count > 0),
            "degraded_services": sum(1 for count in consumer_count.values() if count == 0),
        }

        return {
            "queue_depth": queue_depth,
            "consumer_count": consumer_count,
            "message_rate": message_rate,
            "health_summary": health_summary,
        }

    async def services_health(self) -> list[ServiceHealthItem]:
        overview = await self.metrics_overview()
        now = datetime.now(UTC)
        items: list[ServiceHealthItem] = []
        for queue_name, depth in overview["queue_depth"].items():
            consumers = overview["consumer_count"].get(queue_name, 0)
            items.append(
                ServiceHealthItem(
                    service_name=queue_name,
                    status="healthy" if consumers > 0 else "degraded",
                    latency_ms=int(self._settings.rabbitmq_timeout_seconds * 1000),
                    queue_depth=depth,
                    consumer_count=consumers,
                    captured_at=now,
                )
            )
        return items

    def latest_snapshot_health(self, db: Session) -> list[ServiceHealthItem]:
        stmt = select(ServiceHealthSnapshot).order_by(
            ServiceHealthSnapshot.service_name.asc(), ServiceHealthSnapshot.captured_at.desc()
        )
        snapshots = db.execute(stmt).scalars().all()

        latest_by_service: dict[str, ServiceHealthSnapshot] = {}
        for snapshot in snapshots:
            if snapshot.service_name not in latest_by_service:
                latest_by_service[snapshot.service_name] = snapshot

        return [
            ServiceHealthItem(
                service_name=item.service_name,
                status=item.status,
                latency_ms=item.latency_ms,
                queue_depth=item.queue_depth,
                consumer_count=item.consumer_count,
                captured_at=item.captured_at,
            )
            for item in latest_by_service.values()
        ]

    async def ws_metrics_payload(self, db: Session) -> dict:
        overview = await self.metrics_overview()
        services = await self.services_health()
        interactions = self._build_interactions(overview)
        toggles = await self.service_control_status()
        return {
            "ts": datetime.now(UTC).isoformat(),
            "metrics": {
                "queue_depth": overview["queue_depth"],
                "consumer_count": overview["consumer_count"],
                "message_rate": overview["message_rate"],
                "health_summary": overview["health_summary"],
                "services": [service.model_dump(mode="json") for service in services],
                "interactions": [item.model_dump(mode="json") for item in interactions],
                "toggles": [item.model_dump(mode="json") for item in toggles],
            },
        }

    async def service_control_status(self) -> list[ServiceToggleItem]:
        items: list[ServiceToggleItem] = []
        async with httpx.AsyncClient(timeout=2.0) as client:
            for service_name in SERVICE_CONTROL_ORDER:
                config = SERVICE_ENDPOINTS[service_name]
                base_url = self._service_base_url(service_name)
                enabled = False
                reachable = False
                worker_enabled: bool | None = None
                status = "down"
                message: str | None = None

                try:
                    toggle_resp = await client.get(f"{base_url}{config['toggle_path']}")
                    if toggle_resp.status_code < 400:
                        reachable = True
                        payload = toggle_resp.json()
                        if isinstance(payload, dict):
                            enabled = bool(payload.get("enabled", False))
                except Exception as exc:  # noqa: BLE001
                    message = str(exc)

                try:
                    health = await client.get(f"{base_url}{config['health_path']}")
                    if health.status_code < 400:
                        reachable = True
                        health_json = health.json()
                        if isinstance(health_json, dict):
                            worker_enabled = (
                                bool(health_json.get("worker_enabled"))
                                if "worker_enabled" in health_json
                                else None
                            )
                            if not enabled and worker_enabled is not None:
                                enabled = worker_enabled
                except Exception as exc:  # noqa: BLE001
                    if message is None:
                        message = str(exc)

                if reachable:
                    status = "enabled" if enabled else "disabled"

                items.append(
                    ServiceToggleItem(
                        service_name=service_name,
                        enabled=enabled,
                        reachable=reachable,
                        worker_enabled=worker_enabled,
                        status=status,
                        message=message,
                    )
                )

        return items

    async def set_service_enabled(
        self,
        db: Session,
        service_name: str,
        enabled: bool,
    ) -> ServiceToggleItem:
        service_key = service_name.strip()
        if service_key not in SERVICE_ENDPOINTS:
            raise ApiError(
                error_code="SERVICE_NOT_SUPPORTED",
                message=f"Unsupported service: {service_key}",
                status_code=400,
            )

        config = SERVICE_ENDPOINTS[service_key]
        base_url = self._service_base_url(service_key)

        async with httpx.AsyncClient(timeout=6.0) as client:
            if service_key == "conductor":
                response = await client.post(
                    f"{base_url}{config['toggle_path']}",
                    json={"enabled": enabled},
                )
            else:
                action = "start" if enabled else "stop"
                response = await client.post(f"{base_url}{config['toggle_path']}/{action}")

            if response.status_code >= 400:
                raise ApiError(
                    error_code="SERVICE_TOGGLE_FAILED",
                    message=f"Failed to toggle {service_key} ({response.status_code})",
                    status_code=502,
                )

        instrument = SERVICE_TO_INSTRUMENT.get(service_key)
        if instrument is not None:
            self._audio_renderer.set_instrument_enabled(instrument=instrument, enabled=enabled)
            self._purge_instrument_queue(instrument)

        latest = await self.service_control_status()
        for item in latest:
            if item.service_name == service_key:
                return item

        raise ApiError(
            error_code="SERVICE_STATUS_UNAVAILABLE",
            message=f"Unable to fetch status for {service_key}",
            status_code=503,
        )

    async def snapshot_once(self, db: Session) -> None:
        overview = await self.metrics_overview()
        now = datetime.now(UTC)
        for queue_name, depth in overview["queue_depth"].items():
            consumers = overview["consumer_count"].get(queue_name, 0)
            latency_ms = int(self._settings.rabbitmq_timeout_seconds * 1000)
            status = "healthy" if consumers > 0 else "degraded"
            snapshot = ServiceHealthSnapshot(
                service_name=queue_name,
                status=status,
                latency_ms=latency_ms,
                queue_depth=depth,
                consumer_count=consumers,
                captured_at=now,
            )
            db.add(snapshot)
        db.commit()

    async def _fetch_queues_with_retry(self) -> tuple[list[dict], float]:
        retry_delays = [1, 2, 5]
        for attempt, delay in enumerate([0, *retry_delays], start=1):
            if delay:
                await asyncio.sleep(delay)
            started = time_now_ms()
            try:
                queues, elapsed = await self._metrics_client.fetch_queues()
                LOGGER.info(
                    "rabbitmq_mgmt_poll",
                    extra={
                        "attempt": attempt,
                        "elapsed_ms": round(elapsed, 2),
                        "queues": len(queues),
                    },
                )
                return queues, elapsed
            except httpx.TimeoutException:
                LOGGER.warning(
                    "rabbitmq_mgmt_timeout",
                    extra={"attempt": attempt, "elapsed_ms": round(time_now_ms() - started, 2)},
                )
                continue
            except httpx.HTTPError as exc:
                LOGGER.warning(
                    "rabbitmq_mgmt_error",
                    extra={"attempt": attempt, "error": str(exc)},
                )
                continue

        raise ApiError(
            error_code="RABBITMQ_MGMT_UNAVAILABLE",
            message="Unable to query RabbitMQ Management API",
            status_code=503,
        )

    def _score_file_name(self, source_path: str) -> str:
        return Path(source_path).name

    def _call_conductor_start(self, session_id: UUID, score_path: str, initial_bpm: int) -> None:
        self._call_conductor(
            path="/v1/conductor/start",
            payload={
                "score_path": score_path,
                "initial_bpm": initial_bpm,
                "session_id": str(session_id),
            },
            timeout=12.0,
        )

    def _call_conductor_stop(self, session_id: UUID) -> None:
        self._call_conductor(
            path="/v1/conductor/stop",
            payload={"session_id": str(session_id)},
            timeout=6.0,
        )

    def _call_conductor_tempo(self, session_id: UUID, new_bpm: int, issued_by: str) -> None:
        self._call_conductor(
            path="/v1/conductor/tempo",
            payload={
                "session_id": str(session_id),
                "new_bpm": new_bpm,
                "issued_by": issued_by,
            },
            timeout=6.0,
        )

    def _call_conductor(self, path: str, payload: dict[str, str | int], timeout: float) -> None:
        url = f"{self._settings.conductor_base_url.rstrip('/')}{path}"
        try:
            response = httpx.post(url, json=payload, timeout=timeout)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ApiError(
                error_code="CONDUCTOR_UNAVAILABLE",
                message="Conductor service is unavailable",
                status_code=503,
            ) from exc

    def _service_base_url(self, service_name: str) -> str:
        url_attr = SERVICE_ENDPOINTS[service_name]["url_attr"]
        return str(getattr(self._settings, url_attr)).rstrip("/")

    def _build_interactions(self, overview: dict) -> list[InteractionEdge]:
        queue_depth = overview.get("queue_depth", {})
        consumer_count = overview.get("consumer_count", {})
        message_rate = overview.get("message_rate", {})
        edges: list[InteractionEdge] = []
        for from_service, to_service, queue in QUEUE_FLOW_EDGES:
            edges.append(
                InteractionEdge(
                    from_service=from_service,
                    to_service=to_service,
                    queue=queue,
                    depth=int(queue_depth.get(queue, 0)),
                    consumers=int(consumer_count.get(queue, 0)),
                    message_rate=float(message_rate.get(queue, 0.0)),
                )
            )
        return edges

    def _purge_instrument_queue(self, instrument: str) -> None:
        queue_name = INSTRUMENT_INPUT_QUEUE.get(instrument)
        if queue_name is None:
            return
        connection = None
        channel = None
        try:
            connection = pika.BlockingConnection(pika.URLParameters(self._settings.rabbitmq_url))
            channel = connection.channel()
            channel.queue_purge(queue=queue_name)
        except Exception:
            LOGGER.exception("instrument_queue_purge_failed", extra={"queue": queue_name})
        finally:
            try:
                if channel is not None and channel.is_open:
                    channel.close()
            except Exception:
                pass
            try:
                if connection is not None and connection.is_open:
                    connection.close()
            except Exception:
                pass

    def _resync_running_playback(self, db: Session) -> None:
        stmt = (
            select(PlaybackSession)
            .where(PlaybackSession.status == "running")
            .order_by(PlaybackSession.started_at.desc())
        )
        active = db.execute(stmt).scalars().first()
        if active is None:
            return

        score = db.get(Score, active.score_id)
        if score is None:
            return

        score_file_name = self._score_file_name(score.source_path)
        self._audio_renderer.reset_session()

        try:
            self._call_conductor_stop(active.id)
        except ApiError:
            LOGGER.warning("resync_stop_failed", extra={"session_id": str(active.id)})

        self._call_conductor_start(
            session_id=active.id,
            score_path=score_file_name,
            initial_bpm=active.initial_bpm,
        )

    async def _snapshot_loop(self) -> None:
        from app.db.session import SessionLocal

        interval = self._settings.snapshot_interval_seconds
        while not self._snapshot_stop.is_set():
            try:
                await asyncio.wait_for(self._snapshot_stop.wait(), timeout=interval)
                break
            except TimeoutError:
                pass

            started = time_now_ms()
            db = SessionLocal()
            try:
                await self.snapshot_once(db)
                LOGGER.info(
                    "snapshot_job_cycle",
                    extra={
                        "interval_seconds": interval,
                        "elapsed_ms": round(time_now_ms() - started, 2),
                    },
                )
            except Exception:  # noqa: BLE001
                LOGGER.exception("snapshot_job_failed")
            finally:
                db.close()


def time_now_ms() -> float:
    return datetime.now(UTC).timestamp() * 1000
