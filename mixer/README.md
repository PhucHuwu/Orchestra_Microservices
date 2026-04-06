# Mixer Service

Mixer Service consume `InstrumentOutputEvent` từ queue `instrument.output`, map sang `PlaybackEvent`, sau đó publish vào `playback.output` để IoT playback consume.

## Flow

1. Consume từ `instrument.output` (binding key `instrument.*.output`).
2. Validate payload theo `InstrumentOutputEvent`.
3. Map dữ liệu thành `PlaybackEvent`:
   - `playback_id` sinh mới (UUID)
   - giữ nguyên `note_id`, `instrument`
   - lấy `pitch`, `duration`, `volume` từ `audio_hint`
   - `scheduled_beat_time` lấy từ `scheduled_beat_time` hoặc fallback `beat_time`
   - `emitted_at` là thời điểm mixer publish
4. Publish vào routing key `playback.output` (durable + publisher confirm).
5. Ack input message sau khi publish thành công.

## Reliability

- Queue/exchange khai báo durable.
- Retry publish tối đa 3 lần qua header `x-retry-count`.
- Quá retry sẽ `nack(requeue=False)` để đi DLQ.
- Reconnect RabbitMQ theo backoff: 1s, 2s, 5s, 10s.

## Metrics

- Endpoint: `GET /metrics` (Prometheus format).
- Counter:
  - `mixer_messages_processed_total{instrument=...}`
  - `mixer_mapping_errors_total{instrument=...}`
  - `mixer_publish_errors_total{instrument=...}`
- Histogram:
  - `mixer_event_latency_ms{instrument=...}`

## Environment variables

- `RABBITMQ_URL` (default: `amqp://orchestra:orchestra@rabbitmq:5672/%2F`)
- `EXCHANGE_NAME` (default: `orchestra.events`)
- `INPUT_QUEUE` (default: `instrument.output`)
- `INPUT_ROUTING_KEY` (default: `instrument.*.output`)
- `OUTPUT_QUEUE` (default: `playback.output`)
- `OUTPUT_ROUTING_KEY` (default: `playback.output`)
- `PREFETCH_COUNT` (default: `50`)

## Local run

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Tests

```bash
pytest mixer/tests/test_health.py
pytest mixer/tests/test_mapper.py
pytest mixer/tests/test_integration_queue_flow.py -m integration
```
