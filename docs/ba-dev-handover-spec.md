# Tai lieu BA ban giao cho Dev (Baseline khong IoT)

## 1. Muc tieu tai lieu

Tai lieu nay la baseline de doi dev trien khai dong nhat, tap trung vao he thong microservices event-driven chay local va phat audio tren loa may tinh.

Pham vi gom:

- Kien truc he thong va ranh gioi service.
- Cong nghe su dung (chot phien ban nen tang).
- Database va schema du lieu cot loi.
- API contract va message contract.
- Tieu chi hoan thanh theo tung khoi.

## 2. Nguyen tac BA + SA baseline

Voi bai toan do an, tai lieu nay ket hop vai tro BA + SA baseline de dev co the code ngay, tranh tranh luan ky thuat trong pham vi MVP.

## 3. Kien truc muc tieu

### 3.1 Mo hinh trien khai

- He thong chay local trong LAN.
- Ho tro:
  - 1 may chay 1 service.
  - 1 may chay nhieu service.
- Khong bat buoc cloud/server thue ngoai.

### 3.2 Logical components

- `RabbitMQ` (message broker trung tam).
- `Conductor Service` (doc score, lap lich note, phat event).
- `Instrument Services` (guitar/oboe/drums/bass; xu ly note theo nhac cu).
- `Mixer Service` (gop output tu instrument, publish playback).
- `Dashboard Service` (API + WebSocket + UI giam sat/dieu khien).
- `PostgreSQL` (luu metadata, session, audit, metrics snapshot).
- `Local Audio Renderer` (dashboard backend render WAV va phat tren web player).

### 3.3 Kien truc giao tiep

- Asynchronous: RabbitMQ (AMQP cho toan bo backend).
- Synchronous: REST API (Dashboard dieu khien he thong).
- Realtime UI: WebSocket (day metrics).

## 4. Chot cong nghe

- Runtime services: `Python 3.11+`.
- Broker: `RabbitMQ 3.x` + Management UI.
- Backend API: `FastAPI`.
- Queue client: `pika`.
- Dashboard frontend: `Next.js` (React + TypeScript).
- Database: `PostgreSQL 15+` + `SQLAlchemy` + `Alembic`.
- Container: `Docker` + `Docker Compose`.
- Audio render local: `fluidsynth` + soundfont GM.

### 4.1 Thu vien chot

#### Backend Python

- `fastapi==0.115.0`
- `uvicorn[standard]==0.30.6`
- `pydantic==2.9.2`
- `pydantic-settings==2.5.2`
- `sqlalchemy==2.0.35`
- `alembic==1.13.2`
- `psycopg[binary]==3.2.3`
- `pika==1.3.2`
- `httpx==0.27.2`
- `python-json-logger==2.0.7`
- `tenacity==9.0.0`
- `prometheus-client==0.21.0`
- `mido==1.3.2`

#### Frontend Dashboard

- `next@14.2.15`
- `react@18.3.1`
- `react-dom@18.3.1`
- `typescript@5.6.3`
- `@tanstack/react-query@5.59.20`
- `zustand@5.0.0`
- `zod@3.23.8`
- `axios@1.7.7`
- `react-hook-form@7.53.1`
- `tailwindcss@3.4.14`
- `recharts@2.12.7`

#### Testing va quality gate

- `pytest==8.3.3`
- `pytest-asyncio==0.24.0`
- `pytest-cov==5.0.0`
- `ruff==0.6.9`
- `black==24.10.0`

## 5. Danh muc service va trach nhiem

### 5.1 Conductor Service

- Input: file score MIDI (.mid), lenh tempo.
- Output:
  - Publish `NoteEvent` theo routing key instrument.
  - Publish `HeartbeatEvent` dinh ky.
- API noi bo:
  - `POST /v1/conductor/start`
  - `POST /v1/conductor/stop`
  - `POST /v1/conductor/tempo`
  - `GET /v1/conductor/status`

### 5.2 Instrument Services

- Consume queue theo instrument.
- Xu ly note, tao `InstrumentOutputEvent`.
- Publish output cho Mixer.
- Can idempotency theo `note_id` de tranh xu ly lap khi reconnect.

### 5.3 Mixer Service

- Consume output tu tat ca instrument.
- Chuan hoa va publish `PlaybackEvent` vao `playback.output`.
- Ghi nhan latency xu ly de Dashboard hien thi.

### 5.4 Dashboard Service

- Cung cap API dieu khien playback/BPM.
- Thu thap metrics tu RabbitMQ Management API + service health endpoints.
- Day metrics realtime ra UI.
- Render audio local de phat tren loa may tinh.

### 5.5 Dashboard Frontend

- Man hinh Playback, Tempo, Monitoring, Fault Demo.
- Tich hop API + `WS /ws/metrics`.
- Khong chua business logic xu ly nhac.

## 6. Database design

### 6.1 Muc tieu luu tru

- Luu score metadata de tai chay demo.
- Luu session playback va lich su thay doi BPM.
- Luu snapshot metrics phuc vu bao cao/danh gia.

### 6.2 Schema de xuat

- `scores`
- `playback_sessions`
- `tempo_commands_audit`
- `service_health_snapshots`
- `dead_letter_events`

## 7. Message contract

### 7.1 NoteEvent

- `note_id` (UUID)
- `session_id` (UUID)
- `instrument` (`guitar|oboe|drums|bass`)
- `pitch` (0-127)
- `duration` (giay)
- `volume` (0-127)
- `beat_time` (giay)
- `timestamp` (ISO 8601)

### 7.2 Topology RabbitMQ

- Exchange: `orchestra.events` (topic, durable).
- Queue/binding:
  - `instrument.guitar.note` <- `instrument.guitar.note`
  - `instrument.oboe.note` <- `instrument.oboe.note`
  - `instrument.drums.beat` <- `instrument.drums.beat`
  - `instrument.bass.note` <- `instrument.bass.note`
  - `instrument.output` <- `instrument.*.output`
  - `playback.output` <- `playback.output`
  - `tempo.control` <- `tempo.control`
  - `system.heartbeat` <- `system.heartbeat`

## 8. NFR baseline

- Dashboard thao tac dieu khien < 300ms trong LAN.
- Metrics realtime tre toi da <= 2s so voi stream backend.
- Queue durable + reconnect strategy cho service.
- Demo local khong can phan cung IoT.

## 9. Definition of Done tong

- Conductor publish dung schema/routing key theo BPM.
- 4 instrument service consume doc lap va publish output dung contract.
- Mixer publish `playback.output` on dinh.
- Dashboard hien thi metrics realtime va phat audio local duoc.
- Fault scenarios chinh (lag, crash/recovery, competing, bpm-runtime) chay duoc.
- Tai lieu runbook va huong dan setup day du.
