# Tài liệu BA bàn giao cho Dev (Khung xương triển khai)

## 1. Mục tiêu tài liệu

Tài liệu này là baseline để đội dev triển khai đồng nhất, giảm tranh luận kỹ thuật trong quá trình code. Phạm vi gồm:

- Kiến trúc hệ thống và ranh giới service.
- Công nghệ sử dụng (chốt phiên bản nền tảng).
- Database và schema dữ liệu cốt lõi.
- API contract và message contract.
- Tiêu chí hoàn thành (Definition of Done) theo từng khối.

## 2. Nguyên tắc vai trò BA trong dự án này

Trong chuẩn doanh nghiệp, BA tập trung yêu cầu nghiệp vụ; Solution Architect/Tech Lead chốt chi tiết kỹ thuật. Với đồ án này, áp dụng mô hình gộp **BA + SA baseline** để dev có thể code ngay.

## 3. Kiến trúc mục tiêu (Target Architecture)

### 3.1 Mô hình triển khai

- Hệ thống chạy local trong LAN.
- Hỗ trợ:
  - 1 máy chạy 1 service.
  - 1 máy chạy nhiều service.
- Không bắt buộc cloud/server thuê ngoài.

### 3.2 Logical components

- `RabbitMQ` (message broker trung tâm).
- `Conductor Service` (đọc score, lập lịch note, phát event).
- `Instrument Services` (violin/piano/drums/cello; xử lý note theo nhạc cụ).
- `Mixer Service` (gộp output từ instrument, publish playback).
- `Dashboard Service` (API + WebSocket + UI giám sát/điều khiển).
- `IoT Playback Service` (ESP32 nhận playback và phát âm).
- `PostgreSQL` (lưu metadata, session, audit, metrics snapshot).

### 3.3 Kiến trúc giao tiếp

- Asynchronous: RabbitMQ (AMQP cho backend services, MQTT cho IoT playback).
- Synchronous: REST API (Dashboard điều khiển hệ thống).
- Realtime UI: WebSocket (đẩy metrics, chốt cho baseline).

## 4. Chốt công nghệ

- Runtime services: `Python 3.11+`.
- Broker: `RabbitMQ 3.x` + Management UI.
- Backend API: `FastAPI`.
- Queue client: `pika`.
- Dashboard frontend: `Next.js` (React + TypeScript).
- Database: `PostgreSQL 15+` + `SQLAlchemy` + `Alembic`.
- Container: `Docker` + `Docker Compose`.
- IoT: `ESP32` + `MicroPython` + `umqtt` qua RabbitMQ MQTT plugin (chốt, không dùng thiết bị thay thế trong baseline).

### 4.1 Danh mục thư viện chốt (dev triển khai đúng theo baseline)

#### Backend Python (mọi service)

- `fastapi==0.115.0`
- `uvicorn[standard]==0.30.6`
- `pydantic==2.9.2`
- `pydantic-settings==2.5.2`
- `sqlalchemy==2.0.35`
- `alembic==1.13.2`
- `psycopg[binary]==3.2.3`
- `pika==1.3.2`
- `httpx==0.27.2`
- `python-json-logger==2.0.7`
- `tenacity==9.0.0`
- `prometheus-client==0.21.0`

#### Conductor (đọc MIDI)

- `mido==1.3.2`

#### Frontend Dashboard (Next.js)

- `next@14.2.15`
- `react@18.3.1`
- `react-dom@18.3.1`
- `typescript@5.6.3`
- `@tanstack/react-query@5.59.20`
- `zustand@5.0.0`
- `zod@3.23.8`
- `axios@1.7.7`
- `react-hook-form@7.53.1`
- `tailwindcss@3.4.14`
- `recharts@2.12.7`

#### IoT ESP32 (MicroPython)

- `umqtt.simple` (MQTT client)
- `network` (WiFi)
- `machine` (GPIO/PWM cho buzzer/loa)
- `ujson` (parse payload)
- `utime` (timing/retry backoff)

#### Testing và quality gate

- `pytest==8.3.3`
- `pytest-asyncio==0.24.0`
- `pytest-cov==5.0.0`
- `ruff==0.6.9`
- `black==24.10.0`

## 5. Danh mục service và trách nhiệm

### 5.1 Conductor Service

- Input: file score MIDI (.mid), lệnh tempo.
- Output:
  - Publish `NoteEvent` theo routing key instrument.
  - Publish `HeartbeatEvent` định kỳ.
- API nội bộ:
  - `POST /v1/conductor/start`
  - `POST /v1/conductor/stop`
  - `POST /v1/conductor/tempo`
  - `GET /v1/conductor/status`

### 5.2 Instrument Services (4 service cùng khung)

- Consume queue theo instrument.
- Xử lý note, tạo `InstrumentOutputEvent`.
- Publish output cho Mixer.
- Cần idempotency theo `note_id` để tránh xử lý lặp khi reconnect.

### 5.3 Mixer Service

- Consume output từ tất cả instrument.
- Chuẩn hóa và publish `PlaybackEvent` vào `playback.output`.
- Ghi nhận latency xử lý để Dashboard hiển thị.

### 5.4 Dashboard Service

- Cung cấp API điều khiển playback/BPM.
- Thu thập metrics từ RabbitMQ Management API + service health endpoints.
- Đẩy metrics realtime ra UI.

## 5.6 Dashboard Frontend (FE)

### 5.6.1 Vai trò FE

- Là lớp vận hành trực quan cho người demo.
- Không chứa business logic xử lý nhạc; chỉ gọi API và hiển thị realtime.

### 5.6.2 Màn hình bắt buộc

- **Màn hình Điều khiển Playback**
  - Chọn score, nhập BPM ban đầu, Start/Stop session.
  - Hiển thị trạng thái phiên chạy (`running/stopped/failed`).
- **Màn hình Tempo Realtime**
  - Slider/Input BPM.
  - Nút Apply BPM và hiển thị thời điểm cập nhật gần nhất.
- **Màn hình Giám sát Hệ thống**
  - Queue depth, consumer count, message rate theo từng queue.
  - Health theo service (Conductor/Instrument/Mixer/IoT).
  - Latency tổng quan và cảnh báo ngưỡng.
- **Màn hình Kịch bản lỗi (Fault Demo)**
  - Nút/command preset cho: lag, crash/recovery, scale consumer, IoT reconnect.
  - Ghi nhận timeline sự kiện demo.

### 5.6.3 Contract FE <-> BE

- FE dùng các API ở Mục 9 và stream `WS /ws/metrics`.
- Chuẩn hóa response envelope:
  - Thành công: `{ "success": true, "data": ... }`
  - Lỗi: `{ "success": false, "error_code": "...", "message": "..." }`

### 5.6.4 NFR cho FE

- Thời gian phản hồi thao tác điều khiển (click -> phản hồi UI): `< 300ms` trong LAN.
- Dữ liệu metrics realtime trễ tối đa `<= 2s` so với backend stream.
- UI hiển thị tốt trên desktop (bắt buộc) và tablet (khuyến nghị).

### 5.6.5 Definition of Done cho FE

- Có đủ 4 màn hình bắt buộc.
- Kết nối thành công tất cả API/WS đã định nghĩa.
- Có trạng thái loading/error/empty rõ ràng cho từng widget chính.
- Có thể vận hành đầy đủ một buổi demo mà không cần thao tác CLI.

### 5.5 IoT Playback Service

- Subscribe `playback.output`.
- Kết nối broker bằng MQTT và subscribe topic `playback.output`.
- Nhận `PlaybackEvent`, chuyển thành lệnh phát âm.
- Auto reconnect WiFi + broker, không chứa business logic.

### 5.5.1 Quyết định chốt phần cứng IoT

- Thiết bị chuẩn triển khai: `ESP32`.
- Không mở rộng Raspberry Pi/board khác trong phạm vi baseline.
- Mọi API/message liên quan playback được kiểm thử trên ESP32 làm chuẩn nghiệm thu.

## 6. Database design (PostgreSQL)

### 6.1 Mục tiêu lưu trữ

- Lưu score metadata để tái chạy demo.
- Lưu session playback và lịch sử thay đổi BPM.
- Lưu snapshot metrics phục vụ báo cáo/đánh giá.

### 6.2 Schema đề xuất

#### Bảng `scores`

- `id` UUID PK
- `name` VARCHAR(120)
- `source_type` VARCHAR(20) (`midi`)
- `source_path` TEXT
- `created_at` TIMESTAMP

#### Bảng `playback_sessions`

- `id` UUID PK
- `score_id` UUID FK -> `scores.id`
- `status` VARCHAR(20) (`running`/`stopped`/`failed`)
- `started_at` TIMESTAMP
- `ended_at` TIMESTAMP NULL
- `initial_bpm` INT

#### Bảng `tempo_commands_audit`

- `id` UUID PK
- `session_id` UUID FK -> `playback_sessions.id`
- `old_bpm` INT
- `new_bpm` INT
- `issued_by` VARCHAR(80)
- `issued_at` TIMESTAMP

#### Bảng `service_health_snapshots`

- `id` BIGSERIAL PK
- `service_name` VARCHAR(60)
- `status` VARCHAR(20)
- `latency_ms` INT
- `queue_depth` INT
- `consumer_count` INT
- `captured_at` TIMESTAMP

#### Bảng `dead_letter_events`

- `id` BIGSERIAL PK
- `event_type` VARCHAR(40)
- `source_service` VARCHAR(60)
- `payload` JSONB
- `reason` TEXT
- `created_at` TIMESTAMP

## 7. RabbitMQ topology (chốt)

### 7.1 Exchange

- `orchestra.events` (type: topic, durable)

### 7.2 Queue và routing key

- `instrument.violin.note` <- `instrument.violin.note`
- `instrument.piano.note` <- `instrument.piano.note`
- `instrument.drums.beat` <- `instrument.drums.beat`
- `instrument.cello.note` <- `instrument.cello.note`
- `instrument.output` <- `instrument.*.output`
- `playback.output` <- `playback.output`
- `tempo.control` <- `tempo.control`
- `system.heartbeat` <- `system.heartbeat`

Tất cả queue: `durable = true`, bật DLQ theo từng queue instrument và playback.

## 8. Message schema (contract)

### 8.0 Quy định định dạng dữ liệu đầu vào

- Định dạng đầu vào chuẩn cho Conductor: `MIDI (.mid)`.
- Lý do: phổ biến, dễ tìm dataset công khai, thuận tiện demo và tái sử dụng.
- JSON chỉ dùng nội bộ sau bước parse MIDI, không phải input người dùng trong baseline.

### 8.1 `NoteEvent`

```json
{
  "note_id": "uuid",
  "session_id": "uuid",
  "instrument": "violin|piano|drums|cello",
  "pitch": 60,
  "duration": 0.5,
  "volume": 100,
  "beat_time": 12.5,
  "timestamp": "2026-04-06T10:10:00Z"
}
```

### 8.2 `InstrumentOutputEvent`

```json
{
  "note_id": "uuid",
  "instrument": "violin",
  "rendered_at": "2026-04-06T10:10:00Z",
  "latency_ms": 35,
  "audio_hint": {
    "pitch": 60,
    "duration": 0.5,
    "volume": 100
  }
}
```

### 8.3 `PlaybackEvent`

```json
{
  "playback_id": "uuid",
  "note_id": "uuid",
  "instrument": "violin",
  "pitch": 60,
  "duration": 0.5,
  "volume": 100,
  "scheduled_beat_time": 12.5,
  "emitted_at": "2026-04-06T10:10:00Z"
}
```

### 8.4 `TempoCommand`

```json
{
  "session_id": "uuid",
  "new_bpm": 132,
  "issued_by": "dashboard",
  "issued_at": "2026-04-06T10:10:00Z"
}
```

## 9. API contract (Dashboard/Core)

### 9.1 Điều khiển playback

- `POST /api/v1/playback/start`
  - Request: `{ "score_id": "uuid", "initial_bpm": 120 }`
  - Response: `{ "session_id": "uuid", "status": "running" }`

- `POST /api/v1/playback/stop`
  - Request: `{ "session_id": "uuid" }`
  - Response: `{ "status": "stopped" }`

### 9.2 Điều chỉnh tempo

- `POST /api/v1/tempo`
  - Request: `{ "session_id": "uuid", "new_bpm": 140 }`
  - Response: `{ "status": "accepted" }`

### 9.3 Theo dõi

- `GET /api/v1/metrics/overview`
- `GET /api/v1/services/health`
- `WS /ws/metrics` (stream mỗi 1 giây)

## 10. Quy ước lỗi và độ tin cậy

- Ack message sau khi xử lý thành công.
- Nack + requeue tối đa 3 lần; quá ngưỡng đẩy DLQ.
- Reconnect backoff: 1s, 2s, 5s, 10s (lặp ở 10s).
- Mỗi service phải có health endpoint: `GET /health`.

## 11. NFR chốt để dev triển khai

- End-to-end latency `< 200ms` (LAN bình thường).
- Throughput broker `>= 100 msg/s`.
- Dashboard refresh `1s`.
- Tỷ lệ mất message = 0 trong test restart broker (với queue durable + publisher confirm).

## 12. Definition of Done theo hạng mục

### 12.1 Service-level

- Có Dockerfile, health endpoint, structured log, reconnect logic.
- Pass test unit cơ bản và test integration với RabbitMQ local.

### 12.2 System-level

- Chạy được qua Docker Compose nhiều máy local (LAN).
- Demo được tối thiểu 3 fault scenarios theo rubric.
- Dashboard hiển thị metrics realtime.
- IoT nhận và phát âm từ `playback.output`.
- Dashboard FE điều khiển được start/stop playback và đổi BPM real-time.

## 13. Kế hoạch triển khai khuyến nghị

1. Setup nền tảng: RabbitMQ + DB + Dashboard API skeleton.
2. Làm Conductor + 2 Instrument trước (violin, drums).
3. Hoàn thiện Mixer + IoT playback.
4. Mở rộng đủ 4 instrument.
5. Hoàn thiện metrics, fault injection, tài liệu demo.

## 14. Quy tắc thay đổi yêu cầu

- Mọi thay đổi vào contract (API/schema/message) phải tạo mục **Change Request** trong tài liệu.
- Dev không tự đổi contract nếu chưa cập nhật tài liệu và thông báo toàn đội.
