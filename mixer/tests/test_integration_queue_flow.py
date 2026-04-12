from __future__ import annotations

import os
import socket
import time
from uuid import uuid4

import pika
import pytest
from app.config import Settings
from app.worker import MixerWorker


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


@pytest.mark.integration
def test_mixer_consumes_and_publishes_playback_event() -> None:
    host = os.getenv("RABBITMQ_HOST", "localhost")
    port = int(os.getenv("RABBITMQ_PORT", "5672"))
    if not _rabbitmq_available(host, port):
        pytest.skip("RabbitMQ is not available for integration test")

    rabbitmq_url = os.getenv("RABBITMQ_URL", f"amqp://guest:guest@{host}:{port}/%2F")
    settings = Settings(
        RABBITMQ_URL=rabbitmq_url,
        EXCHANGE_NAME="orchestra.events",
        INPUT_QUEUE="instrument.output",
        OUTPUT_QUEUE="playback.output",
    )
    worker = MixerWorker(settings=settings)
    worker.start()

    connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
    channel = connection.channel()
    channel.exchange_declare(exchange=settings.exchange_name, exchange_type="topic", durable=True)

    payload = {
        "note_id": str(uuid4()),
        "instrument": "guitar",
        "rendered_at": "2026-04-06T10:10:00Z",
        "latency_ms": 20,
        "scheduled_beat_time": 4.5,
        "audio_hint": {"pitch": 60, "duration": 0.5, "volume": 100},
    }
    channel.basic_publish(
        exchange=settings.exchange_name,
        routing_key="instrument.guitar.output",
        body=(
            "{"
            f'"note_id":"{payload["note_id"]}",'
            '"instrument":"guitar",'
            '"rendered_at":"2026-04-06T10:10:00Z",'
            '"latency_ms":20,'
            '"scheduled_beat_time":4.5,'
            '"audio_hint":{"pitch":60,"duration":0.5,"volume":100}'
            "}"
        ).encode(),
        properties=pika.BasicProperties(content_type="application/json", delivery_mode=2),
    )

    deadline = time.time() + 5.0
    got_output = False
    while time.time() < deadline:
        method, _properties, body = channel.basic_get(queue=settings.output_queue, auto_ack=False)
        if method is None:
            time.sleep(0.1)
            continue
        channel.basic_ack(method.delivery_tag)
        if body and payload["note_id"].encode("utf-8") in body:
            got_output = True
            break

    connection.close()
    worker.stop()

    assert got_output is True
