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
