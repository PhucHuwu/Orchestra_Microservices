"""Shared package for Orchestra Microservices."""

from .contracts import Envelope
from .logging import configure_structured_logging, log_context
from .metrics import build_metrics_router
from .rabbitmq import RabbitMQConnectionManager, RabbitMQConsumer, RabbitMQPublisher
from .schemas import BaseEvent

__all__ = [
    "BaseEvent",
    "Envelope",
    "RabbitMQConnectionManager",
    "RabbitMQConsumer",
    "RabbitMQPublisher",
    "build_metrics_router",
    "configure_structured_logging",
    "log_context",
]
