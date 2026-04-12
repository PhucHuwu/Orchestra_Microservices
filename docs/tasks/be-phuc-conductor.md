# Task BE - Phúc (Module Conductor Service)

## 1) Mục tiêu module

Xây dựng `Conductor Service` độc lập: đọc MIDI, lập lịch `NoteEvent`, publish theo đúng routing key, nhận lệnh đổi BPM real-time và phát heartbeat định kỳ.

## 2) Ranh giới trách nhiệm (không chồng chéo)

- Chỉ làm trong thư mục `conductor/`.
- Không sửa code của `services/*`, `mixer/`, `dashboard/`.
- Chỉ dùng contract đã chốt trong tài liệu (`docs/ba-dev-handover-spec.md`).

## 3) Backlog chi tiết (băm nhỏ)

### Trạng thái tổng quan

- ✅ Đã hoàn thành implement: Task 1 -> Task 7
- ⚠️ Cần verify môi trường: chạy full test bằng `pytest` (máy hiện tại chưa có `pytest`)

### Task 1 - Khung service và cấu hình

**Status:** ✅ Done

- Tạo cấu trúc app FastAPI tối thiểu cho Conductor.
- Tạo module config bằng `pydantic-settings`:
  - `RABBITMQ_URL`
  - `EXCHANGE_NAME=orchestra.events`
  - `TEMPO_CONTROL_QUEUE=tempo.control`
  - `HEARTBEAT_QUEUE=system.heartbeat`
- Thêm endpoint `GET /health`.

### Task 2 - MIDI parser

**Status:** ✅ Done

- Tích hợp `mido` để đọc file `.mid` từ `scores/`.
- Map track/note sang `instrument` theo quy tắc rõ ràng.
- Chuẩn hóa thành model `NoteEvent` đúng schema:
  - `note_id`, `session_id`, `instrument`, `pitch`, `duration`, `volume`, `beat_time`, `timestamp`.
- Viết unit test parser với ít nhất 1 file MIDI mẫu.

### Task 3 - Scheduler publish theo BPM

**Status:** ✅ Done

- Xây bộ lập lịch theo `initial_bpm`.
- Publish vào exchange `orchestra.events` với routing key:
  - `instrument.guitar.note`
  - `instrument.oboe.note`
  - `instrument.drums.beat`
  - `instrument.bass.note`
- Bảo đảm thứ tự note trong cùng instrument.
- Bật publisher confirm; log khi publish fail.

### Task 4 - Tempo control runtime

**Status:** ✅ Done (code) / ⚠️ Pending verify integration runtime trên môi trường có RabbitMQ + pytest

- Consume queue `tempo.control`.
- Parse `TempoCommand` và cập nhật BPM runtime không cần restart.
- Audit log các lần đổi BPM (old/new/time).
- Viết integration test mô phỏng đổi BPM khi đang chạy.

### Task 5 - Heartbeat và trạng thái chạy

**Status:** ✅ Done

- Publish heartbeat định kỳ vào `system.heartbeat`.
- Tạo state machine phiên chạy: `running | stopped | failed`.
- Hoàn thiện API nội bộ:
  - `POST /v1/conductor/start`
  - `POST /v1/conductor/stop`
  - `POST /v1/conductor/tempo`
  - `GET /v1/conductor/status`

### Task 6 - Độ tin cậy và logging

**Status:** ✅ Done

- Cài reconnect RabbitMQ theo backoff `1s, 2s, 5s, 10s`.
- Structured log (`python-json-logger`) cho các event chính.
- Xử lý lỗi publish/consume có retry hợp lý.

### Task 7 - Test và tài liệu module

**Status:** ✅ Done (đã viết test + README) / ⚠️ Pending run full test suite do thiếu `pytest` local

- Unit test cho parser, scheduler, tempo update.
- Integration test với RabbitMQ local.
- Viết `conductor/README.md`: cách chạy, env, API, giới hạn hiện tại.

## 4) Definition of Done

- Conductor publish đúng schema + routing key theo BPM.
- Nhận lệnh tempo real-time thành công.
- Có heartbeat, health endpoint, reconnect logic, structured log.
- Test pass và có README module.

**DoD trạng thái hiện tại:**

- ✅ Đạt: 3/4 tiêu chí đầu (publish schema/routing, tempo runtime, heartbeat+health+reconnect+structured log)
- ⚠️ Chưa chốt cuối: cần xác nhận "Test pass" trên môi trường đã cài đủ dependency

