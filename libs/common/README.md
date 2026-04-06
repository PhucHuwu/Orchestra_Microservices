# Common Library

Thư viện dùng chung cho backend services, phục vụ các phần cross-cutting theo baseline:

- RabbitMQ connection manager + publisher/consumer wrapper.
- Structured logging formatter có field observability chuẩn.
- Base schema (Pydantic) và response envelope dùng lại.
- Metrics router mẫu cho endpoint Prometheus `/metrics`.

## Cấu trúc package

- `orchestra_common/schemas.py`: `BaseEvent` (base schema tái sử dụng).
- `orchestra_common/contracts.py`: `Envelope` response contract.
- `orchestra_common/rabbitmq.py`: `RabbitMQConnectionManager`, `RabbitMQPublisher`, `RabbitMQConsumer`.
- `orchestra_common/logging.py`: `configure_structured_logging`, `log_context`.
- `orchestra_common/metrics.py`: `build_metrics_router`.

## Guideline tích hợp theo service

1. Khởi tạo logging ngay lúc startup service:

   ```python
   from orchestra_common import configure_structured_logging

   configure_structured_logging(service_name="conductor")
   ```

2. Dùng context log để đẩy field thống nhất:

   ```python
   from orchestra_common import log_context

   with log_context(event="message_processed", message_id=msg_id, session_id=session_id, latency_ms=latency):
       logger.info("publish_ok")
   ```

3. Dùng connection manager + wrapper khi thao tác RabbitMQ:

   ```python
   manager = RabbitMQConnectionManager(rabbitmq_url=settings.rabbitmq_url)
   publisher = RabbitMQPublisher(manager=manager, exchange_name=settings.exchange_name)
   publisher.publish_json(routing_key="tempo.control", payload=tempo_payload)
   ```

4. Expose endpoint metrics Prometheus:

   ```python
   from fastapi import FastAPI
   from orchestra_common import build_metrics_router

   app = FastAPI()
   app.include_router(build_metrics_router())
   ```

5. Tuân thủ field log chuẩn toàn hệ thống: `service_name`, `event`, `message_id`, `session_id`, `latency_ms`.
