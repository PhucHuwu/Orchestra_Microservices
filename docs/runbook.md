# Runbook vận hành Orchestra Microservices

Tai lieu setup chi tiet 5 may (conductor lam host): `docs/setup-5-nodes.md`.

## 1) Startup toàn hệ thống

1. Chuẩn bị biến môi trường:

   ```bash
   cp .env.example .env
   ```

2. (Khuyến nghị local dev) Tạo virtualenv Python và cài tool:

   - macOS/Linux:

     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     python -m pip install --upgrade pip
     python -m pip install -r requirements-dev.txt
     ```

   - Windows PowerShell:

     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     python -m pip install --upgrade pip
     python -m pip install -r requirements-dev.txt
     ```

3. Khởi chạy stack:

   ```bash
   make up
   ```

4. Bootstrap topology RabbitMQ (idempotent, có thể chạy lại nhiều lần):

   ```bash
   make bootstrap-topology
   ```

5. Xác nhận service chính đã sẵn sàng:

   - RabbitMQ Management: `http://localhost:15672`
   - Dashboard API health: `http://localhost:8000/health`
   - Dashboard UI: `http://localhost:3000`

## 2) Shutdown toàn hệ thống

1. Dọn fault demo nếu đã bật kịch bản:

   ```bash
   make fault-cleanup
   ```

2. Dừng toàn bộ stack:

   ```bash
   make down
   ```

## 3) Kiểm tra nhanh health và queue

1. Kiểm tra container:

   ```bash
   make ps
   ```

2. Kiểm tra API health:

   ```bash
   curl http://localhost:8101/health
   curl http://localhost:8201/health
   curl http://localhost:8202/health
   curl http://localhost:8203/health
   curl http://localhost:8301/health
   curl http://localhost:8000/health
   ```

3. Kiểm tra topology queue trên RabbitMQ UI:

   - Exchange `orchestra.events` tồn tại, type `topic`, durable `true`.
   - Queue chuẩn tồn tại: `instrument.guitar.note`, `instrument.oboe.note`, `instrument.drums.beat`, `instrument.bass.note`, `instrument.output`, `playback.output`, `tempo.control`, `system.heartbeat`.
   - DLQ tồn tại cho các queue instrument và playback: `instrument.guitar.note.dlq`, `instrument.oboe.note.dlq`, `instrument.drums.beat.dlq`, `instrument.bass.note.dlq`, `playback.output.dlq`.

## 4) Pipeline 5 máy (khuyến nghị demo phân tán)

Mô hình triển khai:

- Máy 1: `conductor`
- Máy 2: `mixer`
- Máy 3: `guitar-service`
- Máy 4: `oboe-service`
- Máy 5: `drums-service` (điều khiển nhóm nhạc cụ phụ: `drums` + `bass`)

Yêu cầu mạng:

- Các máy cùng LAN và truy cập được RabbitMQ theo `RABBITMQ_URL`.
- Mỗi máy chỉ chạy đúng service tương ứng (có thể dùng `docker compose up <service-name>`).

Điều phối bật/tắt nhạc cụ:

- Dashboard gọi `POST /api/v1/services/control` để bật/tắt từng instrument service.
- Khi tắt service nhạc cụ, nhạc cụ tương ứng dừng phát ngay.
- Khi bật lại service nhạc cụ, Dashboard tự resync playback đang chạy để đồng bộ lại toàn bộ ban nhạc.
- Với `drums-service`, thao tác bật/tắt sẽ áp dụng cho cả `drums` và `bass`.

## 5) Dùng Prisma cloud để share database

Thiết lập nhanh:

1. Tạo Prisma Postgres instance và lấy connection string.
2. Trong `.env`, gán `DATABASE_URL` trỏ về Prisma cloud (khuyến nghị có `sslmode=require`).
3. Không cần chạy container `postgres` local.

Ví dụ:

```env
DATABASE_URL=postgresql+psycopg://<user>:<password>@<host>:5432/<db>?sslmode=require
```

Chạy stack theo 2 chế độ:

- Không dùng local postgres (dùng Prisma cloud):

  ```bash
  docker compose up --build
  ```

- Dùng local postgres fallback:

  ```bash
  docker compose --profile local-db up --build
  ```

## 6) Expose HTTPS bằng nport

Yêu cầu:

- Node.js >= 20
- Đã cài nport: `npm install -g nport` hoặc dùng `npx`

Expose Dashboard Web (`3000`) và Dashboard API (`8000`):

```bash
nport 3000 -s orchestra-web
nport 8000 -s orchestra-api
```

Sau đó cập nhật `.env` trên máy chạy frontend/backend:

```env
NEXT_PUBLIC_API_BASE_URL=https://orchestra-api.nport.link
NEXT_PUBLIC_WS_URL=wss://orchestra-api.nport.link/ws/metrics
CORS_ALLOW_ORIGINS=https://orchestra-web.nport.link
```

Gợi ý vận hành:

- Giữ terminal nport luôn mở trong suốt buổi demo.
- Nếu subdomain bị chiếm, đổi tên khác với `-s`.

## 7) Fault demo toolkit

Script fault toolkit nằm tại `scripts/fault_injection.py`.

- Chạy toàn bộ kịch bản demo:

  ```bash
  make fault-demo
  ```

- Chạy từng kịch bản:

  ```bash
  python scripts/fault_injection.py run --scenario consumer-lag
  python scripts/fault_injection.py run --scenario service-crash-recovery
  python scripts/fault_injection.py run --scenario competing-consumers
  python scripts/fault_injection.py run --scenario bpm-runtime
  ```

- Cleanup từng kịch bản hoặc toàn bộ:

  ```bash
  python scripts/fault_injection.py cleanup --scenario consumer-lag
  python scripts/fault_injection.py cleanup --scenario service-crash-recovery
  python scripts/fault_injection.py cleanup --scenario competing-consumers
  python scripts/fault_injection.py cleanup --scenario bpm-runtime
  make fault-cleanup
  ```

## 8) Sự cố thường gặp và cách xử lý

- RabbitMQ chưa sẵn sàng khi bootstrap topology:
  - Chờ broker lên hoàn toàn rồi chạy lại `make bootstrap-topology`.
- Service không kết nối được broker:
  - Kiểm tra `RABBITMQ_URL` trong `.env`.
  - Kiểm tra container `rabbitmq` và network `orchestra_net`.
- Queue depth tăng cao, nhạc bị trễ:
  - Kiểm tra kịch bản `consumer-lag` có đang bật không.
  - Cleanup bằng `python scripts/fault_injection.py cleanup --scenario consumer-lag`.
- nport bị ngắt làm frontend không gọi được API:
  - Kiểm tra tiến trình `nport` còn chạy không.
  - Chạy lại `nport` và cập nhật lại URL public nếu subdomain thay đổi.

## 9) Checklist demo trước khi trình bày

- [ ] `make up` chạy thành công, tất cả container `Up`.
- [ ] `make bootstrap-topology` chạy thành công.
- [ ] RabbitMQ UI hiển thị đầy đủ exchange/queue/DLQ.
- [ ] Tối thiểu các endpoint health trả `200`.
- [ ] Dashboard API endpoint `/metrics` trả dữ liệu Prometheus.
- [ ] (Nếu dùng internet demo) URL nport cho web/api truy cập được qua HTTPS.
- [ ] Đã thử 1 kịch bản fault + cleanup thành công.

