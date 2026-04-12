# Phan tich thiet ke he thong theo chuan BA (ban khong IoT)

## 1. Thong tin tai lieu

- Du an: Orchestra Microservices
- Nguon yeu cau: `docs/project.md`
- Muc dich: Chuan hoa phan tich nghiep vu va thiet ke he thong muc logic de lam co so cho SRS, thiet ke ky thuat va demo.

## 2. Boi canh nghiep vu

### 2.1 Van de can giai quyet

Du an can mo phong cac khai niem he thong phan tan theo cach truc quan. Nguoi hoc khong chi nhin metric ma con nghe duoc tac dong cua su co phan tan qua am thanh (lag, crash, out-of-sync, reconnect).

### 2.2 Muc tieu hoc thuat

- Tao he thong microservices co kha nang demo tren laptop/local LAN.
- Minh hoa day du dong su kien qua RabbitMQ theo mo hinh event-driven.
- Chung minh cac khai niem: consumer lag, back-pressure, message durability, reconnect, competing consumers, dynamic configuration.

### 2.3 Gia tri mang lai

- Tang tinh truc quan khi hoc mon he thong phan tan.
- De trinh bay va danh gia trong bai bao cao/do an.
- Co kha nang tai hien su co de phuc vu giang day.

## 3. Pham vi (Scope)

### 3.1 In-scope

- RabbitMQ 3.x (single node) va Management UI (`:15672`).
- Conductor Service.
- Instrument Services (guitar, oboe, drums, bass; toi thieu 2 service hoat dong doc lap).
- Mixer Service tong hop output.
- Dashboard Service theo doi metric real-time.
- Message schema cho `NoteEvent` va luong dieu khien BPM qua `tempo.control`.
- Ho tro trien khai local da may trong LAN: 1 may chay 1 service hoac 1 may chay nhieu service.
- Demo cac kich ban loi co chu dich theo tai lieu.
- Local audio playback tren loa may tinh.

### 3.2 Out-of-scope

- Trien khai production cloud, multi-region, HA cap cao.
- Bao mat cap doanh nghiep (SSO, KMS, PKI day du).
- Yeu cau chat luong am thanh muc chuyen nghiep.
- Thiet bi IoT/firmware rieng.

## 4. Stakeholders va Actors

### 4.1 Stakeholders

- Giang vien/hoi dong cham diem.
- Nhom sinh vien phat trien.
- Nguoi demo van hanh he thong.
- Nguoi xem buoi demo.

### 4.2 System actors

- RabbitMQ Broker.
- Docker runtime (compose).
- Dashboard web client (nguoi van hanh).

## 5. Functional requirements (FR)

- **FR-01 - Score ingestion:** Conductor doc file MIDI (.mid) lam dau vao chuan, parse note event theo BPM.
- **FR-02 - Event publishing:** Conductor publish note vao exchange/queue dung instrument.
- **FR-03 - Tempo control:** Conductor lang nghe `tempo.control` va thay doi BPM real-time.
- **FR-04 - Heartbeat sync:** Conductor phat heartbeat dinh ky de cac service dong bo nhip.
- **FR-05 - Instrument consume/process:** Moi Instrument service consume queue rieng, xu ly note, phat output cho Mixer.
- **FR-06 - Mixing:** Mixer nhan output tu instrument services, tong hop va publish vao `playback.output`.
- **FR-07 - Local playback:** Dashboard backend nhan luong playback, render audio va phat tren loa may tinh.
- **FR-08 - Dashboard monitoring:** Hien thi queue depth, consumer lag, message rate, health service, latency beat.
- **FR-09 - Reconnect handling:** Service tu reconnect khi mat ket noi RabbitMQ/network.
- **FR-10 - Fault demo support:** Ho tro cac kich ban demo loi theo tai lieu yeu cau.
- **FR-11 - Local multi-machine deployment:** Cac service co the chay phan tan tren nhieu may local trong LAN.

## 6. Non-functional requirements (NFR)

### 6.1 Performance

- Do tre end-to-end (Conductor publish -> local playback): `< 200ms` trong LAN thong thuong.
- RabbitMQ xu ly toi thieu `100 msg/s`.
- Dashboard cap nhat metrics moi `1s`.

### 6.2 Reliability

- Queue duoc cau hinh durable.
- Service co reconnect strategy khi mat broker.
- Cau hinh ket noi broker ho tro dia chi mang LAN (khong phu thuoc `localhost`).

### 6.3 Observability

- Dashboard hien thi real-time queue depth, consumer count, message rate.
- Moi service log trang thai ket noi va tong so message da xu ly.
- RabbitMQ Management UI san sang tren cong `15672`.

### 6.4 Constraints

- Chi phi thap, uu tien chay local bang Docker Compose.
- Khong phu thuoc phan cung IoT.
- Khong bat buoc thue server/cloud.

## 7. Use case view

- **UC-01 - Start playback:** Nguoi van hanh khoi dong he thong, nap score, bat dau ban nhac.
- **UC-02 - Change BPM runtime:** Nguoi van hanh gui lenh BPM qua Dashboard, he thong cap nhat toc do ngay.
- **UC-03 - Observe system health:** Nguoi van hanh theo doi metrics va health de phat hien bat thuong.
- **UC-04 - Inject consumer lag:** Co y gay cham instrument service, quan sat queue depth va am thanh lech nhip.
- **UC-05 - Simulate crash/recovery:** Dung service giua chung, khoi dong lai va theo doi backlog replay.
- **UC-06 - Horizontal scale test:** Tang so instance instrument va quan sat competing consumers.

## 8. Domain model (logical)

### 8.1 Thuc the chinh

- `Score`: Nguon du lieu nhac dau vao chuan (MIDI .mid).
- `NoteEvent`: Don vi su kien nhac duoc publish qua broker.
- `TempoCommand`: Lenh thay doi BPM.
- `InstrumentOutput`: Ket qua xu ly note cua tung instrument.
- `PlaybackEvent`: Su kien tong hop sau Mixer gui den local renderer.
- `ServiceHealth`: Trang thai song/chet/latency cua service.
- `QueueMetric`: Queue depth, consumer count, message rate.

### 8.2 Message contract chinh (NoteEvent)

- `note_id` (UUID)
- `instrument` (guitar/oboe/drums/bass)
- `pitch` (0-127)
- `duration` (giay)
- `volume` (0-127)
- `beat_time` (giay)
- `timestamp` (ISO 8601)

## 9. Event flow logic

1. Conductor nap score va sinh `NoteEvent` theo lich beat.
2. Conductor publish vao `orchestra.events` voi routing key theo instrument.
3. Instrument service consume va xu ly note.
4. Instrument publish output den Mixer.
5. Mixer tong hop va publish vao `playback.output`.
6. Dashboard backend consume/render `playback.output` va frontend phat audio.
7. Dashboard lay metric tu RabbitMQ API + service endpoints de hien thi.

Nhanh dieu khien:

1. Dashboard gui `TempoCommand` vao `tempo.control`.
2. Conductor nhan lenh va cap nhat BPM runtime.
3. Luong publish note moi duoc dieu chinh theo BPM moi.

## 10. Logical architecture decomposition

- **Presentation layer:** Dashboard web (FastAPI + WebSocket + Next.js).
- **Application layer:** Conductor, Instrument services, Mixer.
- **Integration layer:** RabbitMQ (topic exchange, durable queues).
- **Playback layer:** Dashboard backend audio renderer.
- **Cross-cutting:** Logging, health check, metrics collection.

## 11. Risk va gap analysis

### 11.1 Rui ro chinh

- Message ordering bi anh huong khi scale competing consumers.
- Do tre vuot nguong 200ms khi queue depth tang cao.
- Mismatch schema giua service gay fail consume.
- Soundfont/audio dependency thieu tren may moi.

### 11.2 Khoang trong yeu cau can bo sung

- Chua dinh nghia ro ack/retry/dead-letter policy cho tung queue.
- Chua chot cach do consumer lag (event-time lag hay queue-depth proxy).
- Chua co acceptance criteria chi tiet dang Given-When-Then cho tung FR.
- Chua co contract ro giua Instrument -> Mixer (ngoai NoteEvent).
- Chua mo ta permission/co che auth RabbitMQ cho role service.

## 12. Requirement traceability matrix (RTM) rut gon

| Requirement | Muc tieu danh gia lien quan | Tieu chi thanh cong |
|---|---|---|
| FR-01, FR-02 | Conductor publish dung note theo BPM | Note dung routing key, dung timestamp/beat |
| FR-05 | Instrument doc lap | It nhat 2 instrument hoat dong doc lap |
| FR-06, FR-07 | Local playback | Dashboard phat dung am thanh tu `playback.output` |
| FR-08 + NFR-Obs | Dashboard monitoring | Cap nhat metric 1s, hien thi health va lag |
| FR-10 | Demo fault scenarios | Trinh bay toi thieu 3 kich ban loi co chu dich |
| NFR-Rel | Message durability/recovery | Queue durable, reconnect thanh cong |
