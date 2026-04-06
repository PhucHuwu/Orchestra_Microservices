from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from datetime import UTC, datetime
from uuid import UUID
from uuid import uuid4

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api import ApiError
from app.config import Settings
from app.db.models import PlaybackSession, Score, ServiceHealthSnapshot, TempoCommandAudit
from app.metrics import RabbitMQManagementClient, parse_queue_stats
from app.rabbitmq_client import RabbitMQPublisher
from app.schemas import ServiceHealthItem

LOGGER = logging.getLogger(__name__)


class DashboardService:
    def __init__(
        self,
        settings: Settings,
        publisher: RabbitMQPublisher,
        metrics_client: RabbitMQManagementClient,
    ) -> None:
        self._settings = settings
        self._publisher = publisher
        self._metrics_client = metrics_client
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
        return {
            "ts": datetime.now(UTC).isoformat(),
            "metrics": {
                "queue_depth": overview["queue_depth"],
                "consumer_count": overview["consumer_count"],
                "message_rate": overview["message_rate"],
                "health_summary": overview["health_summary"],
                "services": [service.model_dump(mode="json") for service in services],
            },
        }

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
