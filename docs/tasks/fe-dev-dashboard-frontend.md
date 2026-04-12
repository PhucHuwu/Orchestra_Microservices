# Task FE - Dashboard Frontend (1 Dev)

## 1) Mục tiêu module

Xây dựng toàn bộ `Dashboard Frontend` (Next.js + TypeScript) để vận hành demo mà không cần thao tác CLI: điều khiển playback, đổi BPM real-time, giám sát hệ thống và chạy kịch bản lỗi.

## 2) Ranh giới trách nhiệm

- Chỉ làm frontend trong `dashboard/` (Next.js app).
- Không chỉnh business logic backend của `conductor/`, `services/*`, `mixer/`.
- Tích hợp đúng API/WS contract đã chốt trong `docs/ba-dev-handover-spec.md`.

## 3) Backlog chi tiết (băm nhỏ)

### Task 1 - Khởi tạo nền tảng FE

- Cấu hình Next.js 14 + TypeScript + Tailwind.
- Thiết lập kiến trúc thư mục:
  - `app/` (routes/pages)
  - `components/`
  - `features/`
  - `lib/api/`, `lib/ws/`
  - `stores/`
- Setup `@tanstack/react-query`, `zustand`, `zod`, `axios`.

### Task 2 - Chuẩn hóa API client và error handling

- Tạo API client dùng chung với `axios`.
- Chuẩn hóa envelope response:
  - success: `{ "success": true, "data": ... }`
  - error: `{ "success": false, "error_code": "...", "message": "..." }`
- Xử lý lỗi thống nhất: timeout, network fail, backend error.

### Task 3 - Màn hình Điều khiển Playback

- UI chọn score + nhập `initial_bpm`.
- Nút `Start` gọi `POST /api/v1/playback/start`.
- Nút `Stop` gọi `POST /api/v1/playback/stop`.
- Hiển thị trạng thái session: `running | stopped | failed`.
- Có trạng thái loading/success/error rõ ràng.

### Task 4 - Màn hình Tempo Realtime

- Tạo slider/input BPM có validate range hợp lý.
- Nút `Apply BPM` gọi `POST /api/v1/tempo`.
- Hiển thị BPM hiện tại + thời điểm cập nhật gần nhất.
- Chặn gửi lệnh khi chưa có session chạy.

### Task 5 - Màn hình Giám sát Hệ thống

- Tích hợp `GET /api/v1/metrics/overview` và `GET /api/v1/services/health`.
- Widget bắt buộc:
  - queue depth
  - consumer count
  - message rate
  - health theo service
  - latency tổng quan
- Biểu đồ realtime bằng `recharts` cho metric chính.

### Task 6 - WebSocket realtime metrics

- Kết nối `WS /ws/metrics`.
- Cập nhật UI mỗi 1 giây.
- Cơ chế reconnect tự động khi mất kết nối.
- Hiển thị trạng thái socket: connected/disconnected/reconnecting.

### Task 7 - Màn hình Kịch bản lỗi (Fault Demo)

- Tạo giao diện trigger preset scenario (qua API backend khi có sẵn):
  - consumer lag
  - crash/recovery
  - scale consumer
  - network reconnect (service-side)
- Hiển thị timeline sự kiện demo theo thứ tự thời gian.

### Task 8 - Trạng thái UX và khả năng dùng demo

- Hoàn thiện trạng thái `loading / empty / error` cho từng widget chính.
- Toast/alert rõ ràng cho thao tác điều khiển.
- Bảo đảm dùng tốt trên desktop (bắt buộc), tablet (khuyến nghị).

### Task 9 - Kiểm thử FE

- Unit test cho util, schema validate, API client.
- Component test cho form playback/tempo.
- Kiểm thử thủ công toàn luồng vận hành demo từ UI.

### Task 10 - Tài liệu module FE

- Viết `dashboard/frontend/README.md`:
  - env cần thiết (`NEXT_PUBLIC_API_BASE_URL`, `NEXT_PUBLIC_WS_URL`)
  - cách chạy local
  - cấu trúc màn hình
  - checklist smoke test trước demo

## 4) Definition of Done

- Có đủ 4 màn hình bắt buộc: Playback, Tempo, Monitoring, Fault Demo.
- Kết nối thành công API + WebSocket theo contract.
- UI phản hồi thao tác nhanh, có trạng thái lỗi/loading/empty đầy đủ.
- Dùng được để vận hành trọn buổi demo mà không cần CLI.
- Có tài liệu chạy và checklist kiểm thử FE.
