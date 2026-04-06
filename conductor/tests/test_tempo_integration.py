from __future__ import annotations

import os
import socket
import time
from pathlib import Path
from uuid import uuid4

import pika
import pytest
from mido import Message, MetaMessage, MidiFile, MidiTrack

from app.config import Settings
from app.models import ConductorStartRequest
from app.service import ConductorRuntime


def _rabbitmq_available(host: str, port: int) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.4)
    try:
        sock.connect((host, port))
        return True
    except OSError:
        return False
    finally:
        sock.close()


def _write_short_midi(path: Path) -> None:
    midi = MidiFile(ticks_per_beat=480)
    track = MidiTrack()
    track.append(MetaMessage("track_name", name="Violin", time=0))
    track.append(Message("note_on", note=60, velocity=100, channel=0, time=0))
    track.append(Message("note_off", note=60, velocity=0, channel=0, time=480))
    track.append(Message("note_on", note=62, velocity=100, channel=0, time=480))
    track.append(Message("note_off", note=62, velocity=0, channel=0, time=480))
    midi.tracks.append(track)
    midi.save(str(path))


@pytest.mark.integration
def test_tempo_command_consumed_during_runtime(tmp_path: Path) -> None:
    host = os.getenv("RABBITMQ_HOST", "localhost")
    port = int(os.getenv("RABBITMQ_PORT", "5672"))
    if not _rabbitmq_available(host, port):
        pytest.skip("RabbitMQ is not available for integration test")

    rabbitmq_url = os.getenv("RABBITMQ_URL", f"amqp://guest:guest@{host}:{port}/%2F")

    score_dir = tmp_path / "scores"
    score_dir.mkdir(parents=True)
    midi_path = score_dir / "tempo_integration.mid"
    _write_short_midi(midi_path)

    settings = Settings(
        RABBITMQ_URL=rabbitmq_url,
        SCORE_DIR=str(score_dir),
        HEARTBEAT_INTERVAL_SECONDS=0.2,
    )
    runtime = ConductorRuntime(settings)
    session_id = uuid4()

    runtime.start(
        ConductorStartRequest(
            score_path="tempo_integration.mid",
            initial_bpm=60,
            session_id=session_id,
        )
    )

    connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
    channel = connection.channel()
    channel.basic_publish(
        exchange=settings.exchange_name,
        routing_key=settings.tempo_control_queue,
        body=(
            "{"
            f'"session_id":"{session_id}",'
            '"new_bpm":150,'
            '"issued_by":"integration-test",'
            '"issued_at":"2026-04-06T10:10:00Z"'
            "}"
        ).encode("utf-8"),
        properties=pika.BasicProperties(content_type="application/json", delivery_mode=2),
    )
    connection.close()

    timeout_at = time.time() + 3.0
    while time.time() < timeout_at:
        status = runtime.status()
        if status.bpm == 150:
            break
        time.sleep(0.1)

    runtime.stop(session_id)
    assert runtime.status().bpm == 150
