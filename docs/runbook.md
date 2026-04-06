# Runbook vận hành Orchestra Microservices

## 1) Startup toàn hệ thống

1. Chuẩn bị biến môi trường:

   ```bash
   cp .env.example .env
   ```

2. Khởi chạy stack:

   ```bash
   make up
   ```

3. Bootstrap topology RabbitMQ (idempotent, có thể chạy lại nhiều lần):

   ```bash
   make bootstrap-topology
   ```

4. Xác nhận service chính đã sẵn sàng:

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
   curl http://localhost:8204/health
   curl http://localhost:8301/health
   curl http://localhost:8000/health
   ```

3. Kiểm tra topology queue trên RabbitMQ UI:

   - Exchange `orchestra.events` tồn tại, type `topic`, durable `true`.
   - Queue chuẩn tồn tại: `instrument.violin.note`, `instrument.piano.note`, `instrument.drums.beat`, `instrument.cello.note`, `instrument.output`, `playback.output`, `tempo.control`, `system.heartbeat`.
   - DLQ tồn tại cho các queue instrument và playback: `instrument.violin.note.dlq`, `instrument.piano.note.dlq`, `instrument.drums.beat.dlq`, `instrument.cello.note.dlq`, `playback.output.dlq`.

## 4) Fault demo toolkit

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
  python scripts/fault_injection.py run --scenario iot-reconnect
  ```

- Cleanup từng kịch bản hoặc toàn bộ:

  ```bash
  python scripts/fault_injection.py cleanup --scenario consumer-lag
  python scripts/fault_injection.py cleanup --scenario service-crash-recovery
  python scripts/fault_injection.py cleanup --scenario competing-consumers
  python scripts/fault_injection.py cleanup --scenario bpm-runtime
  python scripts/fault_injection.py cleanup --scenario iot-reconnect
  make fault-cleanup
  ```

## 5) Sự cố thường gặp và cách xử lý

- RabbitMQ chưa sẵn sàng khi bootstrap topology:
  - Chờ broker lên hoàn toàn rồi chạy lại `make bootstrap-topology`.
- Service không kết nối được broker:
  - Kiểm tra `RABBITMQ_URL` trong `.env`.
  - Kiểm tra container `rabbitmq` và network `orchestra_net`.
- Queue depth tăng cao, nhạc bị trễ:
  - Kiểm tra kịch bản `consumer-lag` có đang bật không.
  - Cleanup bằng `python scripts/fault_injection.py cleanup --scenario consumer-lag`.
- IoT mất kết nối lâu:
  - Chạy cleanup kịch bản `iot-reconnect` để nối lại network cho container `iot-device`.

## 6) Checklist demo trước khi trình bày

- [ ] `make up` chạy thành công, tất cả container `Up`.
- [ ] `make bootstrap-topology` chạy thành công.
- [ ] RabbitMQ UI hiển thị đầy đủ exchange/queue/DLQ.
- [ ] Tối thiểu các endpoint health trả `200`.
- [ ] Dashboard API endpoint `/metrics` trả dữ liệu Prometheus.
- [ ] Đã thử 1 kịch bản fault + cleanup thành công.
