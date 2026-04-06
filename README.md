# Orchestra Microservices

Baseline skeleton for an event-driven Orchestra Microservices project, based on BA handover documents in `docs/`.

## Stack baseline

- Python 3.11+ services (`FastAPI`, `pika`, `SQLAlchemy`, `Alembic`)
- RabbitMQ 3.x (AMQP + MQTT plugin)
- PostgreSQL 15+
- Dashboard API (`FastAPI`) + Dashboard UI (`Next.js 14`)
- IoT playback firmware target: ESP32 MicroPython

## Repository structure

```text
.
├── conductor/
├── services/
│   ├── violin/
│   ├── piano/
│   ├── drums/
│   └── cello/
├── mixer/
├── dashboard/
│   ├── backend/
│   └── frontend/
├── iot-device/
├── scores/
├── libs/common/
├── configs/rabbitmq/
└── docs/
```

## Quick start

1. Copy env file:

   ```bash
   cp .env.example .env
   ```

2. Start all baseline services:

   ```bash
   docker compose up --build
   ```

3. Endpoints:

- RabbitMQ UI: `http://localhost:15672`
- Dashboard API health: `http://localhost:8000/health`
- Dashboard UI: `http://localhost:3000`

## Conda environment

Create and activate Python environment for local development:

```bash
conda env create -f environment.yml
conda activate orchestra-microservices
```

Verify tools:

```bash
python --version
ruff --version
pytest --version
```

## Notes

- This repository currently contains skeleton modules and contracts only.
- Business logic, full API implementation, and demo fault scenarios are intentionally left for feature implementation phases.
