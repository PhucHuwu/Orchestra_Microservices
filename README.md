# Orchestra Microservices (5 Machines)

Simple deployment guide for a 5-node setup.

## Node Roles

- Node A (Host): `rabbitmq`, `conductor`, `dashboard-api`, `dashboard-web`
- Node B: `mixer`
- Node C: `guitar-service`
- Node D: `oboe-service`
- Node E: `drums-service` (auxiliary instruments: `drums` + `bass`)

## Prerequisites

- Docker + Docker Compose on all machines
- Same project folder on all machines
- All machines in the same LAN
- Shared database (recommended: Prisma Postgres cloud)

Windows host notes:

- Docker Desktop must be running (Linux containers mode).
- For topology bootstrap, scripts auto-create `.venv` and install `pika`.
- If no Python runtime exists, install Python (or Python Launcher on Windows).

Quick checks before running scripts:

```bash
docker version
```

```powershell
docker version
py -3 --version
```

## .env Setup (per machine)

You have two options:

1. Automatic (recommended):
   - Just run the one-command script for your role.
   - The script copies `.env.example` to `.env` and fills required values.

2. Manual:
   - Copy `.env.example` to `.env`.
   - Update at least these values:
     - `RABBITMQ_URL=amqp://orchestra:orchestra@<node-a-ip>:5672/%2F`
     - `RABBITMQ_MGMT_API_URL=http://<node-a-ip>:15672/api`
     - `DATABASE_URL=<your shared postgres/prisma url>` (for host node running `dashboard-api`)

Role env templates are available in:

- `configs/5nodes/host.overrides.env`
- `configs/5nodes/mixer.overrides.env`
- `configs/5nodes/guitar.overrides.env`
- `configs/5nodes/oboe.overrides.env`
- `configs/5nodes/aux-node.overrides.env`

## One Command Per Machine

Use Node A IP as host IP (example: `192.168.1.10`).

### Node A (Host)

macOS/Linux:

```bash
./scripts/run-node.sh host 192.168.1.10 cloud 192.168.1.11 192.168.1.12 192.168.1.13 192.168.1.14
```

Windows PowerShell:

```powershell
./scripts/run-node.ps1 -Role host -HostIp 192.168.1.10 -DbMode cloud -MixerIp 192.168.1.11 -GuitarIp 192.168.1.12 -OboeIp 192.168.1.13 -AuxIp 192.168.1.14
```

Use `local` instead of `cloud` if Node A also runs local Postgres.

What the host script does:

- Creates `.env` from `.env.example`
- Fills host/remote service URLs
- Starts required containers
- Creates `.venv` (if missing), installs `pika`, bootstraps RabbitMQ topology
- Tails logs

### Node B (Mixer)

macOS/Linux:

```bash
./scripts/run-node.sh mixer 192.168.1.10
```

Windows PowerShell:

```powershell
./scripts/run-node.ps1 -Role mixer -HostIp 192.168.1.10
```

### Node C (Guitar)

macOS/Linux:

```bash
./scripts/run-node.sh guitar 192.168.1.10
```

Windows PowerShell:

```powershell
./scripts/run-node.ps1 -Role guitar -HostIp 192.168.1.10
```

### Node D (Oboe)

macOS/Linux:

```bash
./scripts/run-node.sh oboe 192.168.1.10
```

Windows PowerShell:

```powershell
./scripts/run-node.ps1 -Role oboe -HostIp 192.168.1.10
```

### Node E (Aux Instruments)

macOS/Linux:

```bash
./scripts/run-node.sh aux 192.168.1.10
```

Windows PowerShell:

```powershell
./scripts/run-node.ps1 -Role aux -HostIp 192.168.1.10
```

## Service UIs

- Conductor control + system logs: `http://<node-a-ip>:8101/ui`
- Guitar local control: `http://<node-c-ip>:8201/ui`
- Oboe local control: `http://<node-d-ip>:8202/ui`
- Aux local control (drums+bass): `http://<node-e-ip>:8203/ui`
- Mixer: no special UI (health only)

## Full Separate Guide

See `docs/setup-5-nodes.md` for detailed setup and troubleshooting.

## Common Errors

- `open //./pipe/dockerDesktopLinuxEngine... The system cannot find the file specified`
  - Docker daemon is not running. Start Docker Desktop and retry.

- `Python was not found`
  - Install Python (or `py` launcher) and rerun the host script.
