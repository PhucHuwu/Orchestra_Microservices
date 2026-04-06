from __future__ import annotations

import json
import time
from collections.abc import Callable
from typing import Any

import pika
from pika.exceptions import AMQPError

BACKOFF_SECONDS = (1, 2, 5, 10)


class RabbitMQPublisher:
    def __init__(
        self,
        rabbitmq_url: str,
        exchange_name: str,
        control_queues: tuple[str, str],
    ) -> None:
        self._rabbitmq_url = rabbitmq_url
        self._exchange_name = exchange_name
        self._control_queues = control_queues
        self._connection: pika.BlockingConnection | None = None
        self._channel: Any | None = None

    def _ensure_connected(self) -> None:
        if self._connection is not None and self._connection.is_open and self._channel is not None:
            return

        attempt = 0
        while True:
            try:
                self._connection = pika.BlockingConnection(pika.URLParameters(self._rabbitmq_url))
                channel = self._connection.channel()
                channel.confirm_delivery()
                channel.exchange_declare(
                    exchange=self._exchange_name, exchange_type="topic", durable=True
                )
                for queue_name in self._control_queues:
                    channel.queue_declare(queue=queue_name, durable=True)
                    channel.queue_bind(
                        exchange=self._exchange_name,
                        queue=queue_name,
                        routing_key=queue_name,
                    )
                self._channel = channel
                return
            except AMQPError:
                delay = BACKOFF_SECONDS[min(attempt, len(BACKOFF_SECONDS) - 1)]
                attempt += 1
                time.sleep(delay)

    def publish_json(self, routing_key: str, payload: dict[str, Any]) -> None:
        self._ensure_connected()
        assert self._channel is not None
        properties = pika.BasicProperties(content_type="application/json", delivery_mode=2)
        body = json.dumps(payload).encode("utf-8")
        try:
            self._channel.basic_publish(
                exchange=self._exchange_name,
                routing_key=routing_key,
                body=body,
                properties=properties,
                mandatory=False,
            )
        except AMQPError:
            self.close()
            self._ensure_connected()
            assert self._channel is not None
            self._channel.basic_publish(
                exchange=self._exchange_name,
                routing_key=routing_key,
                body=body,
                properties=properties,
                mandatory=False,
            )

    def close(self) -> None:
        if self._connection is not None and self._connection.is_open:
            self._connection.close()
        self._connection = None
        self._channel = None


class RabbitMQPublisherProvider:
    def __init__(self, factory: Callable[[], RabbitMQPublisher]) -> None:
        self._factory = factory
        self._publisher: RabbitMQPublisher | None = None

    def get(self) -> RabbitMQPublisher:
        if self._publisher is None:
            self._publisher = self._factory()
        return self._publisher

    def close(self) -> None:
        if self._publisher is not None:
            self._publisher.close()
