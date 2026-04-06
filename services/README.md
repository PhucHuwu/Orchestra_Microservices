# Instrument Services

## Muc tieu

Cum `Instrument Services` gom `violin`, `piano`, `drums`, `cello` dung chung mot worker framework:

- Consume queue durable theo tung nhac cu.
- Validate `NoteEvent`, xu ly idempotency theo `note_id`.
- Publish `InstrumentOutputEvent` ve `instrument.<name>.output`.
- Retry toi da 3 lan, qua nguong day DLQ.

## Bien moi truong

- `RABBITMQ_URL`: AMQP URL den RabbitMQ.
- `EXCHANGE_NAME`: mac dinh `orchestra.events`.
- `SERVICE_NAME`: ten service, vi du `violin-service`.
- `INSTRUMENT_NAME`: `violin|piano|drums|cello`.
- `INPUT_QUEUE`: queue consume theo instrument.
- `OUTPUT_ROUTING_KEY`: routing key publish output theo instrument.
- `PREFETCH_COUNT`: qos prefetch (mac dinh `50`).
- `MAX_RETRIES`: so lan retry toi da truoc khi vao DLQ (mac dinh `3`).
- `INSTRUMENT_WORKER_ENABLED`: bat worker (dat `true`) hoac chi chay API health (mac dinh `false`).

## Queue map

- `violin-service` consume `instrument.violin.note` -> publish `instrument.violin.output`.
- `piano-service` consume `instrument.piano.note` -> publish `instrument.piano.output`.
- `drums-service` consume `instrument.drums.beat` -> publish `instrument.drums.output`.
- `cello-service` consume `instrument.cello.note` -> publish `instrument.cello.output`.

Moi input queue deu co DLQ rieng: `<input_queue>.dlq`.

## Chay tung service

Dung docker compose:

- `docker compose up rabbitmq violin-service`
- `docker compose up rabbitmq piano-service`
- `docker compose up rabbitmq drums-service`
- `docker compose up rabbitmq cello-service`

Neu chay local khong qua compose, can set day du env va dat `INSTRUMENT_WORKER_ENABLED=true`.
