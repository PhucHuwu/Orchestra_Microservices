# Conductor Service

Conductor Service doc MIDI từ thư mục score, chuyển thành `NoteEvent`, publish lên RabbitMQ theo routing key nhạc cụ, nhận lệnh đổi tempo runtime, và phát heartbeat định kỳ.

## Chức năng đã triển khai

- FastAPI app + health endpoint: `GET /health`
- API nội bộ:
  - `POST /v1/conductor/start`
  - `POST /v1/conductor/stop`
  - `POST /v1/conductor/tempo`
  - `GET /v1/conductor/status`
- MIDI parser (`mido`) -> chuẩn hóa `NoteEvent` đúng contract BA
- Scheduler publish theo BPM với publisher confirm
- Tempo control runtime qua queue `tempo.control`
- Heartbeat định kỳ qua queue `system.heartbeat`
- Structured logging (`python-json-logger`)
- Reconnect RabbitMQ theo backoff: `1s, 2s, 5s, 10s`

## Biến môi trường

- `RABBITMQ_URL` (default: `amqp://orchestra:orchestra@rabbitmq:5672/%2F`)
- `EXCHANGE_NAME` (default: `orchestra.events`)
- `TEMPO_CONTROL_QUEUE` (default: `tempo.control`)
- `HEARTBEAT_QUEUE` (default: `system.heartbeat`)
- `SCORE_DIR` (default: `scores`)
- `HEARTBEAT_INTERVAL_SECONDS` (default: `1.0`)
- `PREFETCH_COUNT` (default: `100`)

## API contract

### `POST /v1/conductor/start`

Request:

```json
{
  "score_path": "sample.mid",
  "initial_bpm": 120,
  "session_id": "optional-uuid"
}
```

### `POST /v1/conductor/stop`

Request:

```json
{
  "session_id": "uuid"
}
```

### `POST /v1/conductor/tempo`

Request:

```json
{
  "session_id": "uuid",
  "new_bpm": 132,
  "issued_by": "dashboard"
}
```

### `GET /v1/conductor/status`

Response (ví dụ):

```json
{
  "status": "running",
  "session_id": "uuid",
  "bpm": 132,
  "published_notes": 120,
  "total_notes": 340,
  "last_error": null
}
```

## Quy tắc map MIDI -> instrument

- Dựa vào `track_name`:
  - chứa `guitar` hoặc `violin` -> `guitar`
  - chứa `oboe` hoặc `piano` hoặc `keys` -> `oboe`
  - chứa `drum` hoặc `percussion` -> `drums`
  - chứa `bass` hoặc `cello` -> `bass`
- Nếu channel là `9` -> `drums`
- Fallback theo index track: `guitar -> oboe -> bass -> drums`

## Test

- Unit tests:
  - parser MIDI
  - scheduler publish/routing
  - tempo update runtime
- Integration test:
  - consume `tempo.control` trong lúc session đang chạy (yêu cầu RabbitMQ local)

Chạy test module:

```bash
python3 -m pytest conductor/tests -q
```

## Giới hạn hiện tại

- Tempo consumer dùng pull (`basic_get`) theo chu kỳ ngắn, chưa dùng long-running callback consumer.
- Retry payload tempo giữ qua header `x-retry-count` trong lần republish; vượt 3 lần sẽ NACK về DLQ.
- Trong môi trường container, cần mount hoặc copy `scores/` để chạy score thực tế.
