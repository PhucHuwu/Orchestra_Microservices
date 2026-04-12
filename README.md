# Orchestra Microservices (5 Machines)

Simple deployment guide for a 5-node setup.

## Recommended Order (Do This First)

To avoid network/firewall issues, validate the system in this order:

1. Run everything on Node A (localhost) and confirm UI works.
2. Open firewall ports on Node A.
3. Switch to real LAN IPs and start Nodes B-E.

## Node Roles

- Node A (Host): `rabbitmq`, `conductor`, `dashboard-api`
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
- If Windows locks `.env` (file in use), close editors/terminals watching `.env` and run the command again.

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

Important: do not guess Node A IP. Check it on Node A first.

Windows:

```powershell
ipconfig
```

macOS/Linux:

```bash
ip addr
```

Use the active LAN IPv4 (Wi-Fi/Ethernet) as `HostIp`.

### Node A (Host)

### Step A1 - Guaranteed local run (100% baseline)

Run this first on Node A to verify stack and UI:

```powershell
./scripts/run-node.ps1 -Role host -HostIp 127.0.0.1 -DbMode cloud -MixerIp 127.0.0.1 -GuitarIp 127.0.0.1 -OboeIp 127.0.0.1 -AuxIp 127.0.0.1
```

Check:

- `http://localhost:8101/ui`
- `http://localhost:8101/ui`

If this works, application is healthy.

Note: local Postgres in this stack is internal-only (no host port bind), so it will not conflict with any Postgres already running on your machine.

### Step A2 - Open Node A firewall ports (Windows)

```powershell
netsh advfirewall firewall add rule name="Orchestra Ports" dir=in action=allow protocol=TCP localport=5672,15672,8000,8101,8201,8202,8203,8301
```

### Step A3 - Run host with real LAN IP

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

## Service UI

- Main UI (single control point): `http://<node-a-ip>:8101/ui`
- Optional local service UIs remain available on instrument nodes (`/ui`).
- `dashboard-web` is removed from the startup flow.

## Default Score Behavior

- Default score is `Concierto-De-Aranjuez.mid`.
- Host script copies this file into `scores/` automatically (if missing).
- In Conductor UI, `Start mixer` also auto-starts Conductor playback and triggers Dashboard API playback start.
- If the score is missing in Dashboard DB, Conductor auto-uploads the default score before starting playback.

## True Live Stream

- Main UI `8101/ui` now supports live audio stream over WebSocket: `/v1/conductor/audio/stream`.
- Audio is synthesized continuously from `playback.output` events.
- Toggling instrument services affects stream output in real time (no full file reload).

## Full Separate Guide

See `docs/setup-5-nodes.md` for detailed setup and troubleshooting.

## Common Errors

- `open //./pipe/dockerDesktopLinuxEngine... The system cannot find the file specified`
  - Docker daemon is not running. Start Docker Desktop and retry.

- `Python was not found`
  - Install Python (or `py` launcher) and rerun the host script.

- `curl http://localhost:8101/health` works but `http://<node-a-ip>:8101` fails
  - Wrong LAN IP or Windows Firewall blocked inbound traffic.
  - Re-check Node A IP with `ipconfig` and open firewall ports.
