from __future__ import annotations

import argparse
import json
import os
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pika

STATE_FILE = Path(".fault_state.json")

SCENARIO_CONSUMER_LAG = "consumer-lag"
SCENARIO_SERVICE_CRASH = "service-crash-recovery"
SCENARIO_COMPETING_CONSUMERS = "competing-consumers"
SCENARIO_BPM_RUNTIME = "bpm-runtime"

SCENARIOS = [
    SCENARIO_CONSUMER_LAG,
    SCENARIO_SERVICE_CRASH,
    SCENARIO_COMPETING_CONSUMERS,
    SCENARIO_BPM_RUNTIME,
]


@dataclass(slots=True)
class Context:
    compose_cmd: str
    rabbitmq_url: str
    exchange_name: str
    orchestra_network_name: str
    session_id: str
    bpm_target: int
    bpm_reset: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fault injection toolkit for Orchestra Microservices"
    )
    parser.add_argument("action", choices=["run", "cleanup"])
    parser.add_argument("--scenario", default="all", choices=["all", *SCENARIOS])
    parser.add_argument(
        "--compose-cmd",
        default=os.getenv("ORCHESTRA_COMPOSE_CMD", "docker compose"),
        help="Compose command prefix",
    )
    parser.add_argument(
        "--rabbitmq-url",
        default=os.getenv("RABBITMQ_URL", "amqp://orchestra:orchestra@localhost:5672/%2F"),
    )
    parser.add_argument("--exchange", default=os.getenv("EXCHANGE_NAME", "orchestra.events"))
    parser.add_argument(
        "--orchestra-network",
        default=os.getenv("ORCHESTRA_NETWORK_NAME", "orchestra_net"),
    )
    parser.add_argument("--session-id", default=os.getenv("FAULT_DEMO_SESSION_ID", str(uuid4())))
    parser.add_argument("--bpm-target", type=int, default=140)
    parser.add_argument("--bpm-reset", type=int, default=120)
    return parser.parse_args()


def run_shell(command: str) -> None:
    subprocess.run(command, shell=True, check=True)


def maybe_run_shell(command: str) -> bool:
    result = subprocess.run(command, shell=True)
    return result.returncode == 0


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {}
    return json.loads(STATE_FILE.read_text(encoding="utf-8"))


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def set_state_flag(scenario: str, value: bool) -> None:
    state = load_state()
    state[scenario] = value
    save_state(state)


def publish_json(ctx: Context, routing_key: str, payload: dict) -> None:
    connection = pika.BlockingConnection(pika.URLParameters(ctx.rabbitmq_url))
    try:
        channel = connection.channel()
        channel.exchange_declare(exchange=ctx.exchange_name, exchange_type="topic", durable=True)
        channel.basic_publish(
            exchange=ctx.exchange_name,
            routing_key=routing_key,
            body=json.dumps(payload).encode("utf-8"),
            properties=pika.BasicProperties(content_type="application/json", delivery_mode=2),
            mandatory=False,
        )
    finally:
        connection.close()


def scenario_consumer_lag_run(ctx: Context) -> None:
    run_shell(f"{ctx.compose_cmd} pause guitar-service")
    now = datetime.now(UTC).isoformat()
    for index in range(100):
        payload = {
            "note_id": str(uuid4()),
            "session_id": ctx.session_id,
            "instrument": "guitar",
            "pitch": 60 + (index % 12),
            "duration": 0.25,
            "volume": 90,
            "beat_time": float(index) * 0.25,
            "timestamp": now,
        }
        publish_json(ctx, "instrument.guitar.note", payload)
    set_state_flag(SCENARIO_CONSUMER_LAG, True)


def scenario_consumer_lag_cleanup(ctx: Context) -> None:
    maybe_run_shell(f"{ctx.compose_cmd} unpause guitar-service")
    set_state_flag(SCENARIO_CONSUMER_LAG, False)


def scenario_service_crash_run(ctx: Context) -> None:
    run_shell(f"{ctx.compose_cmd} stop drums-service")
    set_state_flag(SCENARIO_SERVICE_CRASH, True)


def scenario_service_crash_cleanup(ctx: Context) -> None:
    maybe_run_shell(f"{ctx.compose_cmd} up -d drums-service")
    set_state_flag(SCENARIO_SERVICE_CRASH, False)


def scenario_competing_consumers_run(ctx: Context) -> None:
    run_shell(f"{ctx.compose_cmd} up -d --scale guitar-service=3 guitar-service")
    set_state_flag(SCENARIO_COMPETING_CONSUMERS, True)


def scenario_competing_consumers_cleanup(ctx: Context) -> None:
    maybe_run_shell(f"{ctx.compose_cmd} up -d --scale guitar-service=1 guitar-service")
    set_state_flag(SCENARIO_COMPETING_CONSUMERS, False)


def scenario_bpm_runtime_run(ctx: Context) -> None:
    payload = {
        "session_id": ctx.session_id,
        "new_bpm": ctx.bpm_target,
        "issued_by": "fault-toolkit",
        "issued_at": datetime.now(UTC).isoformat(),
    }
    publish_json(ctx, "tempo.control", payload)
    set_state_flag(SCENARIO_BPM_RUNTIME, True)


def scenario_bpm_runtime_cleanup(ctx: Context) -> None:
    payload = {
        "session_id": ctx.session_id,
        "new_bpm": ctx.bpm_reset,
        "issued_by": "fault-toolkit-cleanup",
        "issued_at": datetime.now(UTC).isoformat(),
    }
    publish_json(ctx, "tempo.control", payload)
    set_state_flag(SCENARIO_BPM_RUNTIME, False)


RUN_HANDLERS = {
    SCENARIO_CONSUMER_LAG: scenario_consumer_lag_run,
    SCENARIO_SERVICE_CRASH: scenario_service_crash_run,
    SCENARIO_COMPETING_CONSUMERS: scenario_competing_consumers_run,
    SCENARIO_BPM_RUNTIME: scenario_bpm_runtime_run,
}

CLEANUP_HANDLERS = {
    SCENARIO_CONSUMER_LAG: scenario_consumer_lag_cleanup,
    SCENARIO_SERVICE_CRASH: scenario_service_crash_cleanup,
    SCENARIO_COMPETING_CONSUMERS: scenario_competing_consumers_cleanup,
    SCENARIO_BPM_RUNTIME: scenario_bpm_runtime_cleanup,
}


def resolve_scenarios(raw: str) -> list[str]:
    if raw == "all":
        return SCENARIOS
    return [raw]


def build_context(args: argparse.Namespace) -> Context:
    return Context(
        compose_cmd=args.compose_cmd,
        rabbitmq_url=args.rabbitmq_url,
        exchange_name=args.exchange,
        orchestra_network_name=args.orchestra_network,
        session_id=args.session_id,
        bpm_target=args.bpm_target,
        bpm_reset=args.bpm_reset,
    )


def main() -> int:
    args = parse_args()
    ctx = build_context(args)
    scenarios = resolve_scenarios(args.scenario)

    handlers = RUN_HANDLERS if args.action == "run" else CLEANUP_HANDLERS

    for scenario in scenarios:
        handlers[scenario](ctx)
        print(f"{args.action} {scenario}: done")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
