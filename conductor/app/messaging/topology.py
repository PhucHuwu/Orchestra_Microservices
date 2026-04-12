EXCHANGE_NAME = "orchestra.events"

QUEUES = {
    "instrument.guitar.note": "instrument.guitar.note",
    "instrument.oboe.note": "instrument.oboe.note",
    "instrument.drums.beat": "instrument.drums.beat",
    "instrument.bass.note": "instrument.bass.note",
    "instrument.output": "instrument.*.output",
    "playback.output": "playback.output",
    "tempo.control": "tempo.control",
    "system.heartbeat": "system.heartbeat",
}


def dead_letter_queue_name(queue_name: str) -> str:
    return f"{queue_name}.dlq"


def dead_letter_routing_key(queue_name: str) -> str:
    return dead_letter_queue_name(queue_name)

