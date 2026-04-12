# Orchestra Microservices

Baseline skeleton for an event-driven Orchestra Microservices project, based on BA handover documents in `docs/`.

## Stack baseline

- Python 3.11+ services (`FastAPI`, `pika`, `SQLAlchemy`, `Alembic`)
- RabbitMQ 3.x (AMQP)
- PostgreSQL 15+
- Dashboard API (`FastAPI`) + Dashboard UI (`Next.js 14`)
- Local audio playback via dashboard backend (computer speakers)

## Repository structure

```text
.
├── conductor/
├── services/
│   ├── guitar/
│   ├── oboe/
│   ├── drums/
│   └── bass/
├── mixer/
├── dashboard/
│   ├── backend/
│   └── frontend/
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

## Python virtual environment (venv)

Create and activate Python environment for local development.

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
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

## Quality gate (local pre-merge)

Chạy các lệnh sau trước khi merge:

```bash
make lint
make test
```

Nếu chạy trực tiếp không qua Makefile:

```bash
ruff check .
black --check .
pytest
```
