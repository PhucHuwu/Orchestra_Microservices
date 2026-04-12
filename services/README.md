# Instrument Services

## Muc tieu

Cum `Instrument Services` gom `guitar`, `oboe`, `drums`, `bass` dung chung mot worker framework:

- Consume queue durable theo tung nhac cu.
- Validate `NoteEvent`, xu ly idempotency theo `note_id`.
- Publish `InstrumentOutputEvent` ve `instrument.<name>.output`.
- Retry toi da 3 lan, qua nguong day DLQ.

## Bien moi truong

- `RABBITMQ_URL`: AMQP URL den RabbitMQ.
- `EXCHANGE_NAME`: mac dinh `orchestra.events`.
- `SERVICE_NAME`: ten service, vi du `guitar-service`.
- `INSTRUMENT_NAME`: `guitar|oboe|drums|bass`.
- `INPUT_QUEUE`: queue consume theo instrument.
- `OUTPUT_ROUTING_KEY`: routing key publish output theo instrument.
- `PREFETCH_COUNT`: qos prefetch (mac dinh `50`).
- `MAX_RETRIES`: so lan retry toi da truoc khi vao DLQ (mac dinh `3`).
- `INSTRUMENT_WORKER_ENABLED`: bat worker (dat `true`) hoac chi chay API health (mac dinh `false`).

## Queue map

- `guitar-service` consume `instrument.guitar.note` -> publish `instrument.guitar.output`.
- `oboe-service` consume `instrument.oboe.note` -> publish `instrument.oboe.output`.
- `drums-service` consume `instrument.drums.beat` -> publish `instrument.drums.output`.
- `bass-service` consume `instrument.bass.note` -> publish `instrument.bass.output`.

Moi input queue deu co DLQ rieng: `<input_queue>.dlq`.

## Chay tung service

Dung docker compose:

- `docker compose up rabbitmq guitar-service`
- `docker compose up rabbitmq oboe-service`
- `docker compose up rabbitmq drums-service`
- `docker compose up rabbitmq bass-service`

Neu chay local khong qua compose, can set day du env va dat `INSTRUMENT_WORKER_ENABLED=true`.

