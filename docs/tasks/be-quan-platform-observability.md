# Task BE - Quân (Module Platform & Observability)

## 1) Mục tiêu module

Xây dựng lớp platform dùng chung cho toàn hệ thống: hạ tầng Docker Compose, RabbitMQ topology, thư viện shared cho kết nối/logging/retry và bộ kịch bản fault demo có thể chạy lặp lại.

## 2) Ranh giới trách nhiệm (không chồng chéo)

- Tập trung vào hạ tầng và module dùng chung, không implement business logic trong Conductor/Instrument/Mixer/Dashboard.
- Không chỉnh logic âm nhạc hoặc API nghiệp vụ từng service.
- Làm rõ contract hạ tầng để các dev khác tích hợp.

## 3) Backlog chi tiết (băm nhỏ)

### Task 1 - Docker Compose nền tảng

- Hoàn thiện `docker-compose.yml` cho:
  - RabbitMQ + Management UI
  - PostgreSQL
  - Các service backend (chỉ wiring/network/env)
- Thiết kế network để hỗ trợ chạy đa máy trong LAN.
- Chuẩn hóa `.env.example` toàn dự án.

### Task 2 - RabbitMQ topology bootstrap

- Viết script/init để khai báo:
  - Exchange `orchestra.events` (topic, durable)
  - Toàn bộ queue chuẩn và binding key
  - DLQ cho instrument/playback queue
- Kiểm tra idempotent khi chạy script nhiều lần.

### Task 3 - Shared library dùng chung BE

- Tạo package shared (ví dụ `shared/`):
  - RabbitMQ connection manager + reconnect backoff
  - Publisher/consumer wrapper với ack/nack chuẩn
  - Structured logging formatter
  - Pydantic schema base dùng lại
- Tài liệu guideline tích hợp cho từng service.

### Task 4 - Observability baseline

- Chuẩn hóa log fields chung:
  - `service_name`, `event`, `message_id`, `session_id`, `latency_ms`
- Tạo endpoint/collector mẫu cho Prometheus metrics.
- Hướng dẫn dashboard backend đọc số liệu thống nhất.

### Task 5 - Fault injection toolkit

- Viết script mô phỏng 5 kịch bản demo:
  - consumer lag
  - service crash/recovery
  - competing consumers
  - đổi BPM runtime
  - IoT disconnect/reconnect
- Mỗi script có cleanup để trả môi trường về trạng thái sạch.

### Task 6 - CI quality gate cơ bản

- Thiết lập lệnh kiểm tra chung:
  - lint (`ruff`, `black --check`)
  - test (`pytest`)
- Tạo tài liệu cách chạy local trước khi merge.

### Task 7 - Runbook vận hành và handover

- Viết `docs/runbook.md`:
  - startup/shutdown toàn hệ thống
  - kiểm tra nhanh health và queue
  - xử lý sự cố thường gặp
- Viết checklist demo trước khi trình bày.

## 4) Definition of Done

- Compose chạy được stack nền tảng ổn định.
- RabbitMQ topology + DLQ được bootstrap tự động.
- Có shared library dùng lại cho BE và guideline rõ ràng.
- Có fault toolkit + runbook để demo lặp lại được.
