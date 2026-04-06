# Phân tích thiết kế hệ thống theo chuẩn BA

## 1. Thông tin tài liệu

- Dự án: Orchestra Microservices
- Nguồn yêu cầu: `docs/project.md`
- Mục đích: Chuẩn hóa phân tích nghiệp vụ và thiết kế hệ thống mức logic để làm cơ sở cho SRS, thiết kế kỹ thuật và demo.

## 2. Bối cảnh nghiệp vụ

### 2.1 Vấn đề cần giải quyết

Dự án cần mô phỏng các khái niệm hệ thống phân tán theo cách trực quan. Người học không chỉ nhìn metric mà còn nghe được tác động của sự cố phân tán qua âm thanh (lag, crash, out-of-sync, reconnect).

### 2.2 Mục tiêu kinh doanh/học thuật

- Tạo hệ thống microservices có khả năng demo trên laptop và thiết bị IoT giá rẻ.
- Minh họa đầy đủ dòng sự kiện qua RabbitMQ theo mô hình event-driven.
- Chứng minh các khái niệm: consumer lag, back-pressure, message durability, reconnect, competing consumers, dynamic configuration.

### 2.3 Giá trị mang lại

- Tăng tính trực quan khi học môn hệ thống phân tán.
- Dễ trình bày và đánh giá trong bài báo cáo/đồ án.
- Có khả năng tái hiện sự cố để phục vụ giảng dạy.

## 3. Phạm vi (Scope)

### 3.1 In-scope

- RabbitMQ 3.x (single node) và Management UI (`:15672`).
- Conductor Service.
- Instrument Services (violin, piano, drums, cello; tối thiểu 2 service hoạt động độc lập theo tiêu chí đánh giá).
- Mixer Service tổng hợp output.
- Dashboard Service theo dõi metric real-time.
- IoT Playback Service trên ESP32 subscribe `playback.output` và phát âm.
- Message schema cho `NoteEvent` và luồng điều khiển BPM qua `tempo.control`.
- Hỗ trợ triển khai local đa máy trong LAN: 1 máy chạy 1 service hoặc 1 máy chạy nhiều service.
- Demo các kịch bản lỗi có chủ đích theo tài liệu.

### 3.2 Out-of-scope

- Triển khai production cloud, multi-region, HA cấp cao.
- Bảo mật cấp doanh nghiệp (SSO, KMS, PKI đầy đủ).
- Yêu cầu chất lượng âm thanh mức chuyên nghiệp.

## 4. Stakeholders và Actors

### 4.1 Stakeholders

- Giảng viên/hội đồng chấm điểm.
- Nhóm sinh viên phát triển.
- Người demo vận hành hệ thống.
- Người xem buổi demo.

### 4.2 System actors

- RabbitMQ Broker.
- Docker runtime (compose).
- ESP32 IoT device.

## 5. Functional requirements (FR)

- **FR-01 - Score ingestion:** Conductor đọc file MIDI (.mid) làm đầu vào chuẩn, parse note event theo BPM.
- **FR-02 - Event publishing:** Conductor publish note vào exchange/queue đúng instrument.
- **FR-03 - Tempo control:** Conductor lắng nghe `tempo.control` và thay đổi BPM real-time.
- **FR-04 - Heartbeat sync:** Conductor phát heartbeat định kỳ để các service đồng bộ nhịp.
- **FR-05 - Instrument consume/process:** Mỗi Instrument service consume queue riêng, xử lý note, phát output cho Mixer.
- **FR-06 - Mixing:** Mixer nhận output từ instrument services, tổng hợp và publish vào `playback.output`.
- **FR-07 - IoT playback:** ESP32 subscribe `playback.output` qua MQTT, phát âm theo `pitch`, `duration`, `volume`.
- **FR-08 - Dashboard monitoring:** Hiển thị queue depth, consumer lag, message rate, health service, latency beat.
- **FR-09 - Reconnect handling:** Service và IoT tự reconnect khi mất kết nối RabbitMQ/WiFi.
- **FR-10 - Fault demo support:** Hỗ trợ 5 kịch bản demo lỗi theo tài liệu yêu cầu.
- **FR-11 - Local multi-machine deployment:** Các service có thể chạy phân tán trên nhiều máy local trong cùng LAN, đồng thời hỗ trợ gom nhiều service trên một máy.

## 6. Non-functional requirements (NFR)

### 6.1 Performance

- Độ trễ end-to-end (Conductor publish -> IoT phát): `< 200ms` trong LAN thông thường.
- RabbitMQ xử lý tối thiểu `100 msg/s`.
- Dashboard cập nhật metrics mỗi `1s`.

### 6.2 Reliability

- Queue được cấu hình durable.
- Service có reconnect strategy khi mất broker.
- IoT có reconnect strategy cho WiFi và MQTT.
- Cấu hình kết nối broker phải hỗ trợ địa chỉ mạng LAN (không phụ thuộc `localhost`).

### 6.3 Observability

- Dashboard hiển thị real-time queue depth, consumer count, message rate.
- Mỗi service log trạng thái kết nối và tổng số message đã xử lý.
- RabbitMQ Management UI sẵn sàng trên cổng `15672`.

### 6.4 Constraints

- Chi phí thấp, ưu tiên chạy local bằng Docker Compose.
- IoT device không chứa business logic (chỉ playback).
- Không bắt buộc thuê server/cloud; có thể dùng hoàn toàn máy local trong LAN.

## 7. Use case view

- **UC-01 - Start playback:** Người vận hành khởi động hệ thống, nạp score, bắt đầu bản nhạc.
- **UC-02 - Change BPM runtime:** Người vận hành gửi lệnh BPM qua Dashboard, hệ thống cập nhật tốc độ ngay.
- **UC-03 - Observe system health:** Người vận hành theo dõi metrics và health để phát hiện bất thường.
- **UC-04 - Inject consumer lag:** Cố ý gây chậm instrument service, quan sát queue depth và âm thanh lệch nhịp.
- **UC-05 - Simulate crash/recovery:** Dừng service giữa chừng, khởi động lại và theo dõi backlog replay.
- **UC-06 - IoT reconnect test:** Ngắt WiFi ESP32, kết nối lại và xác nhận phát bù message.
- **UC-07 - Horizontal scale test:** Tăng số instance instrument và quan sát competing consumers.

## 8. Domain model (logical)

### 8.1 Thực thể chính

- `Score`: Nguồn dữ liệu nhạc đầu vào chuẩn (MIDI .mid).
- `NoteEvent`: Đơn vị sự kiện nhạc được publish qua broker.
- `TempoCommand`: Lệnh thay đổi BPM.
- `InstrumentOutput`: Kết quả xử lý note của từng instrument.
- `PlaybackEvent`: Sự kiện tổng hợp sau Mixer gửi đến IoT.
- `ServiceHealth`: Trạng thái sống/chết/latency của service.
- `QueueMetric`: Queue depth, consumer count, message rate.

### 8.2 Message contract chính (NoteEvent)

Theo tài liệu gốc:

- `note_id` (UUID)
- `instrument` (violin/piano/drums/cello)
- `pitch` (0-127)
- `duration` (giây)
- `volume` (0-127)
- `beat_time` (giây)
- `timestamp` (ISO 8601)

## 9. Event flow logic

1. Conductor nạp score và sinh `NoteEvent` theo lịch beat.
2. Conductor publish vào `orchestra.events` với routing key theo instrument.
3. Instrument service consume và xử lý note.
4. Instrument publish output đến Mixer.
5. Mixer tổng hợp và publish vào `playback.output`.
6. IoT consume `playback.output` và phát âm.
7. Dashboard lấy metric từ RabbitMQ API + service logs/endpoint để hiển thị.

Nhánh điều khiển:

1. Dashboard gửi `TempoCommand` vào `tempo.control`.
2. Conductor nhận lệnh và cập nhật BPM runtime.
3. Luồng publish note mới được điều chỉnh theo BPM mới.

## 10. Logical architecture decomposition

- **Presentation layer:** Dashboard web (FastAPI + WebSocket + HTML/JS).
- **Application layer:** Conductor, Instrument services, Mixer.
- **Integration layer:** RabbitMQ (topic exchange, durable queues).
- **Edge/device layer:** ESP32 playback consumer.
- **Cross-cutting:** Logging, health check, metrics collection.

## 11. Risk và gap analysis

### 11.1 Rủi ro chính

- Message ordering bị ảnh hưởng khi scale competing consumers.
- Độ trễ vượt ngưỡng 200ms khi queue depth tăng cao.
- IoT reconnect không ổn định gây ngắt quãng demo.
- Mismatch schema giữa service gây fail consume.

### 11.2 Khoảng trống yêu cầu cần bổ sung

- Chưa định nghĩa rõ ack/retry/dead-letter policy cho từng queue.
- Chưa chốt cách đo consumer lag (event-time lag hay queue-depth proxy).
- Chưa có acceptance criteria chi tiết dạng Given-When-Then cho từng FR.
- Chưa có contract rõ giữa Instrument -> Mixer (ngoài NoteEvent).
- Chưa mô tả permission/cơ chế auth RabbitMQ cho role service.

## 12. Requirement traceability matrix (RTM) rút gọn

| Requirement | Mục tiêu đánh giá liên quan | Tiêu chí thành công |
|---|---|---|
| FR-01, FR-02 | Conductor publish đúng note theo BPM | Note đúng routing key, đúng timestamp/beat |
| FR-05 | Instrument độc lập | Ít nhất 2 instrument hoạt động độc lập |
| FR-06, FR-07 | IoT playback thật | IoT nhận và phát âm thanh từ `playback.output` |
| FR-08 + NFR-Obs | Dashboard monitoring | Cập nhật metric 1s, hiển thị health và lag |
| FR-10 | Demo fault scenarios | Trình bày tối thiểu 3 kịch bản lỗi có chủ đích |
| NFR-Rel | Message durability/recovery | Queue durable, reconnect thành công |
