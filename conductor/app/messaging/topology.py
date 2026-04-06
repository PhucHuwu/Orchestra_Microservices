EXCHANGE_NAME = "orchestra.events"

QUEUES = {
    "instrument.violin.note": "instrument.violin.note",
    "instrument.piano.note": "instrument.piano.note",
    "instrument.drums.beat": "instrument.drums.beat",
    "instrument.cello.note": "instrument.cello.note",
    "instrument.output": "instrument.*.output",
    "playback.output": "playback.output",
    "tempo.control": "tempo.control",
    "system.heartbeat": "system.heartbeat",
}


def dead_letter_queue_name(queue_name: str) -> str:
    return f"{queue_name}.dlq"


def dead_letter_routing_key(queue_name: str) -> str:
    return dead_letter_queue_name(queue_name)
