from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from typing import Any, Callable

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import AMQPError

LOGGER = logging.getLogger(__name__)
BACKOFF_SECONDS = (1, 2, 5, 10)


@dataclass
class RabbitMQConnectionManager:
    rabbitmq_url: str
    prefetch_count: int = 50

    def __post_init__(self) -> None:
        self._connection: pika.BlockingConnection | None = None
        self._channel: BlockingChannel | None = None

    def connect(self) -> BlockingChannel:
        attempt = 0
        while True:
            try:
                self._connection = pika.BlockingConnection(pika.URLParameters(self.rabbitmq_url))
                self._channel = self._connection.channel()
                self._channel.confirm_delivery()
                self._channel.basic_qos(prefetch_count=self.prefetch_count)
                return self._channel
            except AMQPError as exc:
                delay = BACKOFF_SECONDS[min(attempt, len(BACKOFF_SECONDS) - 1)]
                attempt += 1
                LOGGER.warning(
                    "rabbitmq_connect_retry",
                    extra={"delay_seconds": delay, "error": str(exc)},
                )
                time.sleep(delay)

    def channel(self) -> BlockingChannel:
        if self._channel is None or self._connection is None or self._connection.is_closed:
            return self.connect()
        return self._channel

    def close(self) -> None:
        if self._connection is not None and self._connection.is_open:
            self._connection.close()
        self._connection = None
        self._channel = None


@dataclass
class RabbitMQPublisher:
    manager: RabbitMQConnectionManager
    exchange_name: str

    def publish_json(
        self,
        routing_key: str,
        payload: dict[str, Any],
        headers: dict[str, Any] | None = None,
    ) -> None:
        body = json.dumps(payload).encode("utf-8")
        properties = pika.BasicProperties(
            content_type="application/json",
            delivery_mode=2,
            headers=headers or None,
        )
        self.manager.channel().basic_publish(
            exchange=self.exchange_name,
            routing_key=routing_key,
            body=body,
            properties=properties,
            mandatory=False,
        )


@dataclass
class RabbitMQConsumer:
    manager: RabbitMQConnectionManager
    queue_name: str

    def consume(self, callback: Callable[[BlockingChannel, Any, Any, bytes], None]) -> None:
        channel = self.manager.channel()
        channel.basic_consume(queue=self.queue_name, on_message_callback=callback, auto_ack=False)
        channel.start_consuming()

    def ack(self, delivery_tag: int) -> None:
        self.manager.channel().basic_ack(delivery_tag=delivery_tag)

    def nack(self, delivery_tag: int, requeue: bool) -> None:
        self.manager.channel().basic_nack(delivery_tag=delivery_tag, requeue=requeue)
