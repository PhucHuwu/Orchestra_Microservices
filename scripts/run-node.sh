#!/usr/bin/env sh
set -eu

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Required command not found: $1" >&2
    exit 1
  fi
}

ensure_docker_ready() {
  require_command docker
  if ! docker version >/dev/null 2>&1; then
    echo "Docker daemon is not available. Start Docker Desktop/Engine and retry." >&2
    exit 1
  fi
}

bootstrap_topology() {
  PYTHON_CMD=""
  if command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
  elif command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
  fi

  if [ -z "$PYTHON_CMD" ]; then
    echo "WARNING: Python not found. Skip topology bootstrap." >&2
    echo "Run manually later: python scripts/bootstrap_rabbitmq_topology.py" >&2
    return
  fi

  if [ ! -x ".venv/bin/python" ]; then
    "$PYTHON_CMD" -m venv .venv
  fi

  .venv/bin/python -m pip install --upgrade pip >/dev/null
  .venv/bin/python -m pip install pika >/dev/null
  .venv/bin/python scripts/bootstrap_rabbitmq_topology.py
}

cleanup_venv_markers() {
  rm -f .env.bak
}

trap cleanup_venv_markers EXIT

if [ "${1:-}" = "" ] || [ "${2:-}" = "" ]; then
  echo "Usage: ./scripts/run-node.sh <role> <host-ip> [db-mode] [mixer-ip] [guitar-ip] [oboe-ip] [aux-ip]"
  echo "Roles: host | mixer | guitar | oboe | aux"
  echo "db-mode (host only): cloud (default) | local"
  exit 1
fi

ROLE="$1"
HOST_IP="$2"
DB_MODE="${3:-cloud}"
MIXER_IP="${4:-$HOST_IP}"
GUITAR_IP="${5:-$HOST_IP}"
OBOE_IP="${6:-$HOST_IP}"
AUX_IP="${7:-$HOST_IP}"

ensure_docker_ready

cp .env.example .env

replace() {
  KEY="$1"
  VALUE="$2"
  if grep -q "^${KEY}=" .env; then
    sed -i.bak "s|^${KEY}=.*|${KEY}=${VALUE}|" .env
  else
    printf "%s=%s\n" "$KEY" "$VALUE" >> .env
  fi
}

replace RABBITMQ_HOST "$HOST_IP"
replace RABBITMQ_URL "amqp://orchestra:orchestra@${HOST_IP}:5672/%2F"
replace RABBITMQ_MGMT_API_URL "http://${HOST_IP}:15672/api"

case "$ROLE" in
  host)
    replace RABBITMQ_HOST "rabbitmq"
    replace RABBITMQ_URL "amqp://orchestra:orchestra@rabbitmq:5672/%2F"
    replace RABBITMQ_MGMT_API_URL "http://rabbitmq:15672/api"
    replace CONDUCTOR_BASE_URL "http://${HOST_IP}:8101"
    replace CONDUCTOR_SERVICE_URL "http://${HOST_IP}:8101"
    replace MIXER_SERVICE_URL "http://${MIXER_IP}:8301"
    replace GUITAR_SERVICE_URL "http://${GUITAR_IP}:8201"
    replace OBOE_SERVICE_URL "http://${OBOE_IP}:8202"
    replace DRUMS_SERVICE_URL "http://${AUX_IP}:8203"
    replace BASS_SERVICE_URL "http://${AUX_IP}:8203"
    replace NEXT_PUBLIC_API_BASE_URL "http://${HOST_IP}:8000"
    replace NEXT_PUBLIC_WS_URL "ws://${HOST_IP}:8000/ws/metrics"
    replace CORS_ALLOW_ORIGINS "http://${HOST_IP}:3000"

    if [ "$DB_MODE" = "local" ]; then
      docker compose --profile local-db up -d --build rabbitmq postgres conductor dashboard-api dashboard-web
    else
      docker compose up -d --build rabbitmq conductor dashboard-api dashboard-web
    fi
    bootstrap_topology
    docker compose logs -f rabbitmq conductor dashboard-api dashboard-web
    ;;
  mixer)
    docker compose up -d --build --no-deps mixer
    docker compose logs -f mixer
    ;;
  guitar)
    docker compose up -d --build --no-deps guitar-service
    docker compose logs -f guitar-service
    ;;
  oboe)
    docker compose up -d --build --no-deps oboe-service
    docker compose logs -f oboe-service
    ;;
  aux)
    docker compose up -d --build --no-deps drums-service
    docker compose logs -f drums-service
    ;;
  *)
    echo "Invalid role: $ROLE"
    exit 1
    ;;
esac
