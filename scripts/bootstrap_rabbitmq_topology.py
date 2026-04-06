from __future__ import annotations

import argparse
import logging
import os
import time

import pika
from pika.exceptions import AMQPError

BACKOFF_SECONDS = (1, 2, 5, 10)

EXCHANGE_NAME = "orchestra.events"
EXCHANGE_TYPE = "topic"

STANDARD_BINDINGS = {
    "instrument.violin.note": "instrument.violin.note",
    "instrument.piano.note": "instrument.piano.note",
    "instrument.drums.beat": "instrument.drums.beat",
    "instrument.cello.note": "instrument.cello.note",
    "instrument.output": "instrument.*.output",
    "playback.output": "playback.output",
    "tempo.control": "tempo.control",
    "system.heartbeat": "system.heartbeat",
}

DLQ_ENABLED_QUEUES = {
    "instrument.violin.note",
    "instrument.piano.note",
    "instrument.drums.beat",
    "instrument.cello.note",
    "playback.output",
}


def dead_letter_queue_name(queue_name: str) -> str:
    return f"{queue_name}.dlq"


def dead_letter_routing_key(queue_name: str) -> str:
    return dead_letter_queue_name(queue_name)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bootstrap RabbitMQ topology for Orchestra Microservices"
    )
    parser.add_argument(
        "--rabbitmq-url",
        default=os.getenv("RABBITMQ_URL", "amqp://orchestra:orchestra@localhost:5672/%2F"),
        help="AMQP connection URL",
    )
    parser.add_argument(
        "--exchange",
        default=os.getenv("EXCHANGE_NAME", EXCHANGE_NAME),
        help="Exchange name",
    )
    return parser.parse_args()


def connect_with_backoff(rabbitmq_url: str) -> pika.BlockingConnection:
    attempt = 0
    while True:
        try:
            return pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
        except AMQPError as exc:
            delay = BACKOFF_SECONDS[min(attempt, len(BACKOFF_SECONDS) - 1)]
            attempt += 1
            logging.warning("rabbitmq_connect_retry delay=%s error=%s", delay, exc)
            time.sleep(delay)


def declare_topology(
    channel: pika.adapters.blocking_connection.BlockingChannel, exchange: str
) -> None:
    channel.exchange_declare(exchange=exchange, exchange_type=EXCHANGE_TYPE, durable=True)

    for queue_name, routing_key in STANDARD_BINDINGS.items():
        queue_arguments = None
        if queue_name in DLQ_ENABLED_QUEUES:
            dlq_name = dead_letter_queue_name(queue_name)
            channel.queue_declare(queue=dlq_name, durable=True)
            channel.queue_bind(
                exchange=exchange,
                queue=dlq_name,
                routing_key=dead_letter_routing_key(queue_name),
            )

            queue_arguments = {
                "x-dead-letter-exchange": exchange,
                "x-dead-letter-routing-key": dead_letter_routing_key(queue_name),
            }

        channel.queue_declare(queue=queue_name, durable=True, arguments=queue_arguments)
        channel.queue_bind(exchange=exchange, queue=queue_name, routing_key=routing_key)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = parse_args()

    connection = connect_with_backoff(args.rabbitmq_url)
    try:
        channel = connection.channel()
        declare_topology(channel=channel, exchange=args.exchange)
        logging.info("topology_bootstrap_done exchange=%s", args.exchange)
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
