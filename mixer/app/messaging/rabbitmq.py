from __future__ import annotations

import json
import logging
import time
from typing import Any

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import AMQPError

from app.config import Settings
from app.messaging.topology import EXCHANGE_TYPE, dead_letter_queue_name, dead_letter_routing_key

LOGGER = logging.getLogger(__name__)
BACKOFF_SECONDS = (1, 2, 5, 10)


class RabbitMQClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._connection: pika.BlockingConnection | None = None
        self._channel: BlockingChannel | None = None

    def connect(self) -> None:
        attempt = 0
        while True:
            try:
                self._connection = pika.BlockingConnection(
                    pika.URLParameters(self._settings.rabbitmq_url)
                )
                self._channel = self._connection.channel()
                self._channel.confirm_delivery()
                self._channel.basic_qos(prefetch_count=self._settings.prefetch_count)
                self._declare_topology()
                LOGGER.info("rabbitmq_connected", extra={"service": self._settings.service_name})
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
        self._channel = None
        self._connection = None

    def basic_get(self, queue: str) -> tuple[Any, Any, bytes | None]:
        channel = self._require_channel()
        return channel.basic_get(queue=queue, auto_ack=False)

    def ack(self, delivery_tag: int) -> None:
        self._require_channel().basic_ack(delivery_tag=delivery_tag)

    def nack(self, delivery_tag: int, requeue: bool) -> None:
        self._require_channel().basic_nack(delivery_tag=delivery_tag, requeue=requeue)

    def publish_json(
        self,
        routing_key: str,
        payload: dict[str, Any],
        headers: dict[str, Any] | None = None,
    ) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.publish_raw(routing_key=routing_key, body=body, headers=headers)

    def publish_raw(
        self,
        routing_key: str,
        body: bytes,
        headers: dict[str, Any] | None = None,
    ) -> None:
        properties = pika.BasicProperties(
            content_type="application/json",
            delivery_mode=2,
            headers=headers or None,
        )

        try:
            self._require_channel().basic_publish(
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
            self._require_channel().basic_publish(
                exchange=self._settings.exchange_name,
                routing_key=routing_key,
                body=body,
                properties=properties,
                mandatory=False,
            )

    def _require_channel(self) -> BlockingChannel:
        if self._channel is None or self._connection is None or self._connection.is_closed:
            self.connect()
        assert self._channel is not None
        return self._channel

    def _declare_topology(self) -> None:
        channel = self._require_channel()
        channel.exchange_declare(
            exchange=self._settings.exchange_name,
            exchange_type=EXCHANGE_TYPE,
            durable=True,
        )

        input_dlq = dead_letter_queue_name(self._settings.input_queue)
        channel.queue_declare(queue=input_dlq, durable=True)
        channel.queue_bind(
            exchange=self._settings.exchange_name,
            queue=input_dlq,
            routing_key=dead_letter_routing_key(self._settings.input_queue),
        )

        channel.queue_declare(
            queue=self._settings.input_queue,
            durable=True,
            arguments={
                "x-dead-letter-exchange": self._settings.exchange_name,
                "x-dead-letter-routing-key": dead_letter_routing_key(self._settings.input_queue),
            },
        )
        channel.queue_bind(
            exchange=self._settings.exchange_name,
            queue=self._settings.input_queue,
            routing_key=self._settings.input_routing_key,
        )

        output_dlq = dead_letter_queue_name(self._settings.output_queue)
        channel.queue_declare(queue=output_dlq, durable=True)
        channel.queue_bind(
            exchange=self._settings.exchange_name,
            queue=output_dlq,
            routing_key=dead_letter_routing_key(self._settings.output_queue),
        )
        channel.queue_declare(
            queue=self._settings.output_queue,
            durable=True,
            arguments={
                "x-dead-letter-exchange": self._settings.exchange_name,
                "x-dead-letter-routing-key": dead_letter_routing_key(self._settings.output_queue),
            },
        )
        channel.queue_bind(
            exchange=self._settings.exchange_name,
            queue=self._settings.output_queue,
            routing_key=self._settings.output_routing_key,
        )
