from __future__ import annotations

import json
import logging
import time
from typing import Any

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import AMQPError

from app.config import Settings
from app.messaging.topology import QUEUES, dead_letter_queue_name, dead_letter_routing_key

LOGGER = logging.getLogger(__name__)
BACKOFF_SECONDS = (1, 2, 5, 10)


class RabbitMQPublisher:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._connection: pika.BlockingConnection | None = None
        self._channel: BlockingChannel | None = None

    def connect(self) -> None:
        attempt = 0
        while True:
            try:
                parameters = pika.URLParameters(self._settings.rabbitmq_url)
                self._connection = pika.BlockingConnection(parameters)
                self._channel = self._connection.channel()
                self._channel.confirm_delivery()
                self._channel.exchange_declare(
                    exchange=self._settings.exchange_name,
                    exchange_type="topic",
                    durable=True,
                )
                for queue_name, routing_key in QUEUES.items():
                    dlq_name = dead_letter_queue_name(queue_name)
                    self._channel.queue_declare(queue=dlq_name, durable=True)
                    self._channel.queue_bind(
                        exchange=self._settings.exchange_name,
                        queue=dlq_name,
                        routing_key=dead_letter_routing_key(queue_name),
                    )

                    queue_arguments = {
                        "x-dead-letter-exchange": self._settings.exchange_name,
                        "x-dead-letter-routing-key": dead_letter_routing_key(queue_name),
                    }
                    self._channel.queue_declare(
                        queue=queue_name,
                        durable=True,
                        arguments=queue_arguments,
                    )
                    self._channel.queue_bind(
                        exchange=self._settings.exchange_name,
                        queue=queue_name,
                        routing_key=routing_key,
                    )
                LOGGER.info("rabbitmq_connected", extra={"url": self._settings.rabbitmq_url})
                return
            except AMQPError as exc:
                delay = BACKOFF_SECONDS[min(attempt, len(BACKOFF_SECONDS) - 1)]
                attempt += 1
                LOGGER.warning(
                    "rabbitmq_connect_retry",
                    extra={"delay_seconds": delay, "error": str(exc)},
                )
                time.sleep(delay)

    def close(self) -> None:
        if self._connection is not None and self._connection.is_open:
            self._connection.close()
        self._connection = None
        self._channel = None

    def publish_json(self, routing_key: str, payload: dict[str, Any]) -> None:
        if self._channel is None or self._connection is None or self._connection.is_closed:
            self.connect()

        body = json.dumps(payload).encode("utf-8")
        properties = pika.BasicProperties(content_type="application/json", delivery_mode=2)

        try:
            assert self._channel is not None
            self._channel.basic_publish(
                exchange=self._settings.exchange_name,
                routing_key=routing_key,
                body=body,
                properties=properties,
                mandatory=False,
            )
        except AMQPError:
            LOGGER.exception("publish_failed", extra={"routing_key": routing_key})
            self.close()
            self.connect()
            assert self._channel is not None
            self._channel.basic_publish(
                exchange=self._settings.exchange_name,
                routing_key=routing_key,
                body=body,
                properties=properties,
                mandatory=False,
            )


def create_tempo_consumer_channel(
    settings: Settings,
) -> tuple[pika.BlockingConnection, BlockingChannel]:
    attempt = 0
    while True:
        try:
            connection = pika.BlockingConnection(pika.URLParameters(settings.rabbitmq_url))
            channel = connection.channel()
            channel.exchange_declare(
                exchange=settings.exchange_name,
                exchange_type="topic",
                durable=True,
            )
            queue_arguments = {
                "x-dead-letter-exchange": settings.exchange_name,
                "x-dead-letter-routing-key": dead_letter_routing_key(settings.tempo_control_queue),
            }
            channel.queue_declare(
                queue=settings.tempo_control_queue,
                durable=True,
                arguments=queue_arguments,
            )
            channel.queue_bind(
                exchange=settings.exchange_name,
                queue=settings.tempo_control_queue,
                routing_key=settings.tempo_control_queue,
            )
            dlq_name = dead_letter_queue_name(settings.tempo_control_queue)
            channel.queue_declare(queue=dlq_name, durable=True)
            channel.queue_bind(
                exchange=settings.exchange_name,
                queue=dlq_name,
                routing_key=dead_letter_routing_key(settings.tempo_control_queue),
            )
            channel.basic_qos(prefetch_count=settings.prefetch_count)
            return connection, channel
        except AMQPError as exc:
            delay = BACKOFF_SECONDS[min(attempt, len(BACKOFF_SECONDS) - 1)]
            attempt += 1
            LOGGER.warning(
                "tempo_consumer_connect_retry",
                extra={"delay_seconds": delay, "error": str(exc)},
            )
            time.sleep(delay)
