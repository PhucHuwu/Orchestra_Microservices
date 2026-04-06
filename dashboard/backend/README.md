# Dashboard Backend

Dashboard backend cung cấp API điều khiển playback/tempo, thu thập metrics từ RabbitMQ Management API, stream realtime qua WebSocket, và lưu audit/snapshot vào PostgreSQL.

## Chức năng chính

- `GET /health`
- `GET /metrics` (Prometheus)
- `POST /api/v1/playback/start`
- `POST /api/v1/playback/stop`
- `POST /api/v1/tempo`
- `GET /api/v1/scores`
- `POST /api/v1/scores/upload` (multipart form, field `file`)
- `GET /api/v1/playback/audio/latest` (WAV file, generated from selected MIDI on start)
- `GET /api/v1/metrics/overview`
- `GET /api/v1/services/health`
- `WS /ws/metrics` (push mỗi 1 giây)

Response envelope chuẩn:

- Thành công: `{ "success": true, "data": ... }`
- Lỗi: `{ "success": false, "error_code": "...", "message": "..." }`

## Biến môi trường

- `SERVICE_NAME` (default: `dashboard-api`)
- `DATABASE_URL` (default: `postgresql+psycopg://orchestra:orchestra@postgres:5432/orchestra`)
- `RABBITMQ_URL` (default: `amqp://orchestra:orchestra@rabbitmq:5672/%2F`)
- `RABBITMQ_MGMT_API_URL` (default: `http://rabbitmq:15672/api`)
- `RABBITMQ_MGMT_USERNAME` (optional, fallback từ `RABBITMQ_URL`)
- `RABBITMQ_MGMT_PASSWORD` (optional, fallback từ `RABBITMQ_URL`)
- `EXCHANGE_NAME` (default: `orchestra.events`)
- `TEMPO_CONTROL_QUEUE` (default: `tempo.control`)
- `PLAYBACK_CONTROL_QUEUE` (default: `playback.control`)
- `METRICS_STREAM_INTERVAL_SECONDS` (default: `1.0`)
- `SNAPSHOT_INTERVAL_SECONDS` (default: `5.0`)
- `RABBITMQ_TIMEOUT_SECONDS` (default: `2.0`)
- `CONDUCTOR_BASE_URL` (default: `http://conductor:8000`)
- `SCORE_STORAGE_DIR` (default: `/shared-scores`)
- `AUDIO_OUTPUT_DIR` (default: `/shared-audio`)
- `AUDIO_INPUT_QUEUE` (default: `audio.render.input`)
- `AUDIO_INPUT_ROUTING_KEY` (default: `playback.output`)
- `AUDIO_SAMPLE_RATE` (default: `22050`)
- `CORS_ALLOW_ORIGINS` (default: `http://localhost:3000`)

## Chạy local

Từ root project:

```bash
docker compose up -d rabbitmq postgres
```

Từ thư mục `dashboard/backend`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Migration

- File migration: `alembic/versions/0001_initial_schema.py`
- Tạo các bảng:
  - `scores`
  - `playback_sessions`
  - `tempo_commands_audit`
  - `service_health_snapshots`
  - `dead_letter_events`
- Seed tối thiểu 1 score mẫu vào `scores`

## Test

Từ root project:

```bash
python3 -m pytest dashboard/backend/tests -q
```

Nếu chưa có `pytest` trên môi trường local, cài dependencies trong virtualenv trước khi chạy test.
