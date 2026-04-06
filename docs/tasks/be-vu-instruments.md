# Task BE - Vũ (Module Instrument Services)

## 1) Mục tiêu module

Xây dựng cụm `Instrument Services` (violin, piano, drums, cello) theo một khung chung, mỗi service consume queue riêng, xử lý note, phát `InstrumentOutputEvent` cho Mixer.

## 2) Ranh giới trách nhiệm (không chồng chéo)

- Chỉ làm trong `services/violin/`, `services/piano/`, `services/drums/`, `services/cello/` và thư viện dùng chung nội bộ instrument.
- Không sửa `conductor/`, `mixer/`, `dashboard/`, `iot-device/`.
- Không thay đổi message contract đã chốt.

## 3) Backlog chi tiết (băm nhỏ)

### Task 1 - Tạo framework dùng chung cho 4 instrument

- Tạo base worker dùng `pika`:
  - Kết nối broker
  - Consume queue durable
  - Ack/Nack + retry
- Config hóa bằng env:
  - `INSTRUMENT_NAME`
  - `INPUT_QUEUE`
  - `OUTPUT_ROUTING_KEY=instrument.<name>.output`

### Task 2 - Triển khai 4 worker độc lập

- Violin consume `instrument.violin.note`.
- Piano consume `instrument.piano.note`.
- Drums consume `instrument.drums.beat`.
- Cello consume `instrument.cello.note`.
- Mỗi worker có Dockerfile riêng và endpoint `GET /health`.

### Task 3 - Xử lý `NoteEvent` và idempotency

- Validate payload theo schema `NoteEvent`.
- Tạo cơ chế chống xử lý trùng theo `note_id`.
- Với message lỗi format: ghi log rõ nguyên nhân, đẩy flow lỗi theo policy.

### Task 4 - Phát `InstrumentOutputEvent`

- Chuẩn hóa output event:
  - `note_id`, `instrument`, `rendered_at`, `latency_ms`, `audio_hint`.
- Publish về routing key `instrument.<name>.output` để Mixer consume.
- Đảm bảo ack chỉ sau khi publish output thành công.

### Task 5 - Retry, DLQ, reconnect

- Nack + requeue tối đa 3 lần.
- Quá ngưỡng đẩy DLQ của từng queue instrument.
- Reconnect RabbitMQ theo backoff chuẩn dự án.

### Task 6 - Logging, metric nội bộ, test

- Structured log cho vòng đời message (received/processed/failed).
- Counter nội bộ: số message nhận, thành công, lỗi, trùng lặp.
- Unit test cho parser/validator/idempotency.
- Integration test cho flow consume -> output publish.

### Task 7 - Tài liệu triển khai instrument

- Viết `services/README.md` (hoặc README riêng từng service):
  - Env config
  - Queue map
  - Cách chạy độc lập từng instrument

## 4) Definition of Done

- 4 instrument chạy độc lập, đúng queue subscribe.
- Output event đúng schema gửi về Mixer.
- Có idempotency, retry/DLQ, reconnect, health endpoint.
- Test cơ bản pass và có tài liệu vận hành.

## 5) Trạng thái cập nhật

- [x] Task 1 - Tạo framework dùng chung cho 4 instrument.
- [x] Task 2 - Triển khai 4 worker độc lập (violin/piano/drums/cello) + health endpoint.
- [x] Task 3 - Xử lý `NoteEvent` và idempotency theo `note_id`.
- [x] Task 4 - Phát `InstrumentOutputEvent` đúng schema và routing key output.
- [x] Task 5 - Retry, DLQ, reconnect theo policy (max retry 3, backoff 1/2/5/10).
- [x] Task 6 - Structured logging, counter nội bộ, bổ sung unit test parser/validator/idempotency và flow xử lý.
- [x] Task 7 - Hoàn thiện tài liệu triển khai tại `services/README.md`.

### Ghi chú xác minh

- Đã hoàn tất implementation theo tài liệu.
- Chưa xác minh pass test ngay trên môi trường hiện tại do thiếu `pytest`/`ruff` trong runtime local.
