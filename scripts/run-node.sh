#!/usr/bin/env sh
set -eu

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
    python scripts/bootstrap_rabbitmq_topology.py
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
