# Task BE - Lực (Module Dashboard Backend)

## 1) Mục tiêu module

Xây dựng backend cho Dashboard: API điều khiển playback/tempo, thu thập metrics hệ thống, stream realtime qua WebSocket và ghi dữ liệu audit/snapshot vào PostgreSQL.

## 2) Ranh giới trách nhiệm (không chồng chéo)

- Chỉ làm trong backend của `dashboard/` (FastAPI) và phần DB migration liên quan dashboard.
- Không sửa `conductor/`, `services/*`, `mixer/`, `iot-device/`.
- Không làm frontend Next.js trong phạm vi task này.

## 3) Backlog chi tiết (băm nhỏ)

### Task 1 - Nền tảng API và cấu hình

- Khởi tạo FastAPI app cho dashboard backend.
- Cấu hình env:
  - `DATABASE_URL`
  - `RABBITMQ_URL`
  - `RABBITMQ_MGMT_API_URL`
- Tạo `GET /health` cho service.

### Task 2 - Database model và migration

- Tạo model + Alembic migration cho các bảng:
  - `scores`
  - `playback_sessions`
  - `tempo_commands_audit`
  - `service_health_snapshots`
  - `dead_letter_events`
- Seed dữ liệu score mẫu tối thiểu.

### Task 3 - API điều khiển playback/tempo

- Implement endpoint:
  - `POST /api/v1/playback/start`
  - `POST /api/v1/playback/stop`
  - `POST /api/v1/tempo`
- Publish command tương ứng sang queue/control channel.
- Ghi audit tempo vào `tempo_commands_audit`.

### Task 4 - API theo dõi và tổng hợp trạng thái

- Implement:
  - `GET /api/v1/metrics/overview`
  - `GET /api/v1/services/health`
- Thu dữ liệu từ RabbitMQ Management API.
- Chuẩn hóa response envelope:
  - success: `{ "success": true, "data": ... }`
  - error: `{ "success": false, "error_code": "...", "message": "..." }`

### Task 5 - WebSocket realtime metrics

- Implement `WS /ws/metrics` push mỗi 1 giây.
- Broadcast queue depth, consumer count, message rate, health summary.
- Đảm bảo cơ chế reconnect client an toàn.

### Task 6 - Snapshot và job nền

- Tạo job định kỳ lưu `service_health_snapshots`.
- Cơ chế retry khi RabbitMQ Management API timeout.
- Log rõ chu kỳ poll và thời gian phản hồi.

### Task 7 - Test và tài liệu module

- Unit test cho service layer và validation schema.
- Integration test cho API chính và WebSocket stream.
- Viết `dashboard/backend/README.md` hướng dẫn run + migrate + env.

## 4) Definition of Done

- API playback/tempo hoạt động đúng contract.
- API metrics/health và WS realtime hoạt động ổn định.
- DB migration đầy đủ, ghi audit/snapshot đúng.
- Có health endpoint, test cơ bản pass, tài liệu rõ ràng.
