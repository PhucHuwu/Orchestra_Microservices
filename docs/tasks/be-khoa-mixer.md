# Task BE - Khoa (Module Mixer Service)

## 1) Mục tiêu module

Xây dựng `Mixer Service` độc lập: nhận output từ các instrument, chuẩn hóa thành `PlaybackEvent`, publish vào `playback.output` cho IoT consume.

## 2) Ranh giới trách nhiệm (không chồng chéo)

- Chỉ làm trong thư mục `mixer/`.
- Không sửa `conductor/`, `services/*`, `dashboard/`, `iot-device/`.
- Không đổi contract `InstrumentOutputEvent` và `PlaybackEvent`.

## 3) Backlog chi tiết (băm nhỏ)

### Trạng thái tổng quan

- ✅ Đã hoàn thành implement: Task 1 -> Task 7
- ⚠️ Cần verify thêm integration E2E khi RabbitMQ local chạy sẵn (test integration hiện có cơ chế `skip` nếu broker chưa sẵn sàng)

### Task 1 - Khởi tạo service và config

**Status:** ✅ Done

- Tạo app/service runner cho Mixer.
- Config env:
  - `INPUT_QUEUE=instrument.output`
  - `OUTPUT_QUEUE=playback.output`
  - `EXCHANGE_NAME=orchestra.events`
- Tạo endpoint `GET /health`.

### Task 2 - Consumer instrument output

**Status:** ✅ Done

- Consume `instrument.output` (binding `instrument.*.output`).
- Validate payload `InstrumentOutputEvent`.
- Chuẩn hóa lỗi input, không làm crash worker.

### Task 3 - Mapping sang `PlaybackEvent`

**Status:** ✅ Done

- Map trường dữ liệu:
  - `playback_id` (new UUID)
  - `note_id`, `instrument`, `pitch`, `duration`, `volume`
  - `scheduled_beat_time`, `emitted_at`
- Bảo toàn thông tin từ `audio_hint`.

### Task 4 - Publish playback output

**Status:** ✅ Done

- Publish event vào `playback.output`.
- Bảo đảm durable + publisher confirm.
- Ack message input sau khi publish thành công.

### Task 5 - Tính latency và metric nội bộ

**Status:** ✅ Done

- Tính `latency_ms` từ `rendered_at` đến thời điểm mixer emit.
- Ghi metric tổng hợp theo instrument:
  - throughput
  - lỗi mapping
  - lỗi publish
- Expose metric endpoint (nếu baseline đang dùng Prometheus).

### Task 6 - Reliability và DLQ

**Status:** ✅ Done

- Retry policy cho publish fail.
- Nack/requeue tối đa 3 lần, quá ngưỡng vào DLQ.
- Reconnect broker theo backoff chuẩn dự án.

### Task 7 - Test và tài liệu module

**Status:** ✅ Done (code + test + README) / ⚠️ Pending verify integration khi có RabbitMQ local sẵn sàng

- Unit test mapper `InstrumentOutputEvent -> PlaybackEvent`.
- Integration test queue flow end-to-end qua RabbitMQ local.
- Viết `mixer/README.md` mô tả flow và env.

## 4) Definition of Done

- Mixer consume ổn định từ `instrument.output`.
- Publish `PlaybackEvent` đúng schema vào `playback.output`.
- Có health, metric nội bộ, retry/DLQ, reconnect.
- Test pass và có README module.

**DoD trạng thái hiện tại:**

- ✅ Đạt: 3/4 tiêu chí đầu (consume ổn định, publish đúng schema, health + metric + retry/DLQ + reconnect)
- ⚠️ Chờ chốt cuối: xác nhận integration test end-to-end trong môi trường RabbitMQ local luôn sẵn sàng
