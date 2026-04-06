from __future__ import annotations

import json
import math
import threading
import time
import wave
from pathlib import Path
from typing import Any

import pika
from pika.exceptions import AMQPError

from app.config import Settings

BACKOFF_SECONDS = (1, 2, 5, 10)


class PlaybackAudioRenderer:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._output_dir = Path(settings.audio_output_dir).resolve()
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._latest_file = self._output_dir / "latest.wav"

        self._sample_rate = settings.audio_sample_rate
        self._samples: list[int] = []
        self._samples_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    @property
    def latest_file_path(self) -> Path:
        return self._latest_file

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=3)

    def _run(self) -> None:
        attempt = 0
        while not self._stop_event.is_set():
            connection: pika.BlockingConnection | None = None
            channel = None
            try:
                connection = pika.BlockingConnection(pika.URLParameters(self._settings.rabbitmq_url))
                channel = connection.channel()
                channel.exchange_declare(
                    exchange=self._settings.exchange_name,
                    exchange_type="topic",
                    durable=True,
                )
                channel.queue_declare(queue=self._settings.audio_input_queue, durable=True)
                channel.queue_bind(
                    exchange=self._settings.exchange_name,
                    queue=self._settings.audio_input_queue,
                    routing_key=self._settings.audio_input_routing_key,
                )

                attempt = 0
                while not self._stop_event.is_set():
                    method, _, body = channel.basic_get(
                        queue=self._settings.audio_input_queue,
                        auto_ack=False,
                    )
                    if method is None:
                        time.sleep(0.05)
                        continue

                    try:
                        payload = json.loads(body.decode("utf-8"))
                        pitch = int(payload.get("pitch", 60))
                        duration = float(payload.get("duration", 0.2))
                        volume = int(payload.get("volume", 80))
                        self._append_note(pitch=pitch, duration=duration, volume=volume)
                        channel.basic_ack(delivery_tag=method.delivery_tag)
                    except Exception:
                        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            except AMQPError:
                delay = BACKOFF_SECONDS[min(attempt, len(BACKOFF_SECONDS) - 1)]
                attempt += 1
                time.sleep(delay)
            finally:
                if channel is not None and channel.is_open:
                    channel.close()
                if connection is not None and connection.is_open:
                    connection.close()

    def _append_note(self, pitch: int, duration: float, volume: int) -> None:
        safe_pitch = max(0, min(127, pitch))
        safe_duration = max(0.03, min(4.0, duration))
        safe_volume = max(0, min(127, volume))

        frequency = 440.0 * (2 ** ((safe_pitch - 69) / 12))
        sample_count = int(self._sample_rate * safe_duration)
        amplitude = int((safe_volume / 127.0) * 12000)

        note_samples: list[int] = []
        for i in range(sample_count):
            t = i / self._sample_rate
            note_samples.append(int(amplitude * math.sin(2 * math.pi * frequency * t)))

        silence_count = int(self._sample_rate * 0.01)
        note_samples.extend([0] * silence_count)

        with self._samples_lock:
            self._samples.extend(note_samples)
            self._write_latest_locked()

    def _write_latest_locked(self) -> None:
        with wave.open(str(self._latest_file), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self._sample_rate)
            frames = bytearray()
            for sample in self._samples:
                clamped = max(-32768, min(32767, sample))
                frames.extend(int(clamped).to_bytes(2, byteorder="little", signed=True))
            wav_file.writeframes(frames)
