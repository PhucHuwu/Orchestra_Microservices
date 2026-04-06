# Task BE - Khoa (Module Mixer Service)

## 1) Mục tiêu module

Xây dựng `Mixer Service` độc lập: nhận output từ các instrument, chuẩn hóa thành `PlaybackEvent`, publish vào `playback.output` cho IoT consume.

## 2) Ranh giới trách nhiệm (không chồng chéo)

- Chỉ làm trong thư mục `mixer/`.
- Không sửa `conductor/`, `services/*`, `dashboard/`, `iot-device/`.
- Không đổi contract `InstrumentOutputEvent` và `PlaybackEvent`.

## 3) Backlog chi tiết (băm nhỏ)

### Task 1 - Khởi tạo service và config

- Tạo app/service runner cho Mixer.
- Config env:
  - `INPUT_QUEUE=instrument.output`
  - `OUTPUT_QUEUE=playback.output`
  - `EXCHANGE_NAME=orchestra.events`
- Tạo endpoint `GET /health`.

### Task 2 - Consumer instrument output

- Consume `instrument.output` (binding `instrument.*.output`).
- Validate payload `InstrumentOutputEvent`.
- Chuẩn hóa lỗi input, không làm crash worker.

### Task 3 - Mapping sang `PlaybackEvent`

- Map trường dữ liệu:
  - `playback_id` (new UUID)
  - `note_id`, `instrument`, `pitch`, `duration`, `volume`
  - `scheduled_beat_time`, `emitted_at`
- Bảo toàn thông tin từ `audio_hint`.

### Task 4 - Publish playback output

- Publish event vào `playback.output`.
- Bảo đảm durable + publisher confirm.
- Ack message input sau khi publish thành công.

### Task 5 - Tính latency và metric nội bộ

- Tính `latency_ms` từ `rendered_at` đến thời điểm mixer emit.
- Ghi metric tổng hợp theo instrument:
  - throughput
  - lỗi mapping
  - lỗi publish
- Expose metric endpoint (nếu baseline đang dùng Prometheus).

### Task 6 - Reliability và DLQ

- Retry policy cho publish fail.
- Nack/requeue tối đa 3 lần, quá ngưỡng vào DLQ.
- Reconnect broker theo backoff chuẩn dự án.

### Task 7 - Test và tài liệu module

- Unit test mapper `InstrumentOutputEvent -> PlaybackEvent`.
- Integration test queue flow end-to-end qua RabbitMQ local.
- Viết `mixer/README.md` mô tả flow và env.

## 4) Definition of Done

- Mixer consume ổn định từ `instrument.output`.
- Publish `PlaybackEvent` đúng schema vào `playback.output`.
- Có health, metric nội bộ, retry/DLQ, reconnect.
- Test pass và có README module.
