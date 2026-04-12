# Setup 5 may (Conductor lam host)

Tai lieu nay dung cho mo hinh khong co server rieng. May chay `conductor` dong vai tro host ha tang trong LAN.

## 1) So do phan vai

- May A (host): `rabbitmq`, `conductor`, `dashboard-api`, `dashboard-web` (va `postgres` neu khong dung cloud DB).
- May B: `mixer`.
- May C: `guitar-service`.
- May D: `oboe-service`.
- May E: `drums-service` (cum nhac cu phu: `drums` + `bass`).

Vi du IP LAN:

- May A: `192.168.1.10`
- May B: `192.168.1.11`
- May C: `192.168.1.12`
- May D: `192.168.1.13`
- May E: `192.168.1.14`

## 2) File mau env theo vai tro

Da tao san file mau:

- `configs/5nodes/host.overrides.env`
- `configs/5nodes/mixer.overrides.env`
- `configs/5nodes/guitar.overrides.env`
- `configs/5nodes/oboe.overrides.env`
- `configs/5nodes/aux-node.overrides.env`

Ban co the tham chieu cac file nay de kiem tra mapping IP va URL tung node.

Ngoai ra, script startup se tu tao `.env` tu `.env.example` va tu dong dien cac bien can thiet theo role.

### 2.1 May A (host conductor)

- `RABBITMQ_URL=amqp://orchestra:orchestra@192.168.1.10:5672/%2F`
- `RABBITMQ_MGMT_API_URL=http://192.168.1.10:15672/api`
- `CONDUCTOR_BASE_URL=http://192.168.1.10:8101`
- `CONDUCTOR_SERVICE_URL=http://192.168.1.10:8101`
- `MIXER_SERVICE_URL=http://192.168.1.11:8301`
- `GUITAR_SERVICE_URL=http://192.168.1.12:8201`
- `OBOE_SERVICE_URL=http://192.168.1.13:8202`
- `DRUMS_SERVICE_URL=http://192.168.1.14:8203`
- DB:
  - Neu Prisma cloud: set `DATABASE_URL` cloud.
  - Neu local postgres tren may A: de `DATABASE_URL` ve `postgres` container nhu mac dinh.

### 2.2 May B/C/D/E (node worker)

- `RABBITMQ_URL=amqp://orchestra:orchestra@192.168.1.10:5672/%2F`
- `EXCHANGE_NAME=orchestra.events`
- Khong can sua `DATABASE_URL` neu may do khong chay `dashboard-api`.

## 3) Chay moi may bang 1 cau lenh

Script da tao:

- macOS/Linux: `scripts/run-node.sh`
- Windows PowerShell: `scripts/run-node.ps1`

Luu y:

- May host chay lenh se tu dong: build/up service, bootstrap topology, va tail logs.
- May worker chay lenh se tu dong: build/up dung service role do, va tail logs.

### 3.1 May A (host conductor)

macOS/Linux:

```bash
./scripts/run-node.sh host 192.168.1.10 cloud 192.168.1.11 192.168.1.12 192.168.1.13 192.168.1.14
```

Windows PowerShell:

```powershell
./scripts/run-node.ps1 -Role host -HostIp 192.168.1.10 -DbMode cloud -MixerIp 192.168.1.11 -GuitarIp 192.168.1.12 -OboeIp 192.168.1.13 -AuxIp 192.168.1.14
```

Neu host dung local Postgres, doi `cloud` -> `local` (hoac `-DbMode local`).

### 3.2 May B (mixer)

macOS/Linux:

```bash
./scripts/run-node.sh mixer 192.168.1.10
```

Windows PowerShell:

```powershell
./scripts/run-node.ps1 -Role mixer -HostIp 192.168.1.10
```

### 3.3 May C (guitar)

macOS/Linux:

```bash
./scripts/run-node.sh guitar 192.168.1.10
```

Windows PowerShell:

```powershell
./scripts/run-node.ps1 -Role guitar -HostIp 192.168.1.10
```

### 3.4 May D (oboe)

macOS/Linux:

```bash
./scripts/run-node.sh oboe 192.168.1.10
```

Windows PowerShell:

```powershell
./scripts/run-node.ps1 -Role oboe -HostIp 192.168.1.10
```

### 3.5 May E (aux instruments)

macOS/Linux:

```bash
./scripts/run-node.sh aux 192.168.1.10
```

Windows PowerShell:

```powershell
./scripts/run-node.ps1 -Role aux -HostIp 192.168.1.10
```

`drums-service` tren may E se chay 2 worker: `drums` + `bass`.

## 4) Kiem tra ket noi lien may

Tu may A:

```bash
curl http://192.168.1.10:8101/health
curl http://192.168.1.11:8301/health
curl http://192.168.1.12:8201/health
curl http://192.168.1.13:8202/health
curl http://192.168.1.14:8203/health
curl http://192.168.1.10:8000/health
```

RabbitMQ UI tren host: `http://192.168.1.10:15672`

Giao dien web toi gian:

- Conductor control + system logs: `http://192.168.1.10:8101/ui`
- Guitar service toggle UI: `http://192.168.1.12:8201/ui`
- Oboe service toggle UI: `http://192.168.1.13:8202/ui`
- Aux service toggle UI (drums+bass): `http://192.168.1.14:8203/ui`

Mixer khong can UI dac biet, chi can health:

- `http://192.168.1.11:8301/health`

## 5) Dieu khien bat/tat service va dong bo lai

- Dashboard API: `POST /api/v1/services/control`
- Tat `guitar-service`/`oboe-service`/`drums-service` -> nhac cu tuong ung dung.
- Bat lai service -> dashboard tu dong resync session playback dang chay.
- Voi `drums-service`, bat/tat se ap dung cho ca `drums` va `bass`.

Conductor co the dieu phoi bat/tat tu xa qua API:

- `GET /v1/conductor/services`
- `POST /v1/conductor/services/control`

Vi du payload:

```json
{
  "service_name": "guitar-service",
  "enabled": false
}
```
