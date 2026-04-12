from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from mido import MidiFile

from app.models import ParsedNote


@dataclass(slots=True)
class _PendingNote:
    start_tick: int
    velocity: int
    instrument: str


def _instrument_from_program(program: int) -> str | None:
    if 0 <= program <= 7:
        return "oboe"
    if 24 <= program <= 31:
        return "guitar"
    if 32 <= program <= 39:
        return "bass"
    if 40 <= program <= 41:
        return "guitar"
    if 42 <= program <= 43:
        return "bass"
    if 48 <= program <= 55:
        return "oboe"
    if 68 <= program <= 71:
        return "oboe"
    return None


def _instrument_from_track(
    track_name: str,
    channel: int | None,
    track_index: int,
    channel_programs: dict[int, int],
) -> str:
    lowered = track_name.lower()
    if "guitar" in lowered or "violin" in lowered:
        return "guitar"
    if "oboe" in lowered or "piano" in lowered or "keys" in lowered:
        return "oboe"
    if "string" in lowered:
        return "oboe"
    if "drum" in lowered or "percussion" in lowered:
        return "drums"
    if "bass" in lowered or "cello" in lowered:
        return "bass"

    if channel == 9:
        return "drums"

    if channel is not None and channel in channel_programs:
        inferred = _instrument_from_program(channel_programs[channel])
        if inferred is not None:
            return inferred

    fallback = ("guitar", "oboe", "bass", "drums")
    return fallback[track_index % len(fallback)]


def parse_midi_file(score_path: str, score_dir: str = "scores") -> list[ParsedNote]:
    base_dir = Path(score_dir).resolve()
    full_path = (base_dir / score_path).resolve()
    if not str(full_path).startswith(str(base_dir)):
        raise ValueError("Invalid score_path outside score directory")
    if not full_path.exists():
        raise FileNotFoundError(f"Score file not found: {full_path}")

    midi = MidiFile(str(full_path))
    notes: list[tuple[int, int, ParsedNote]] = []

    for track_index, track in enumerate(midi.tracks):
        absolute_tick = 0
        track_name = ""
        channel_programs: dict[int, int] = {}
        pending: dict[tuple[int, int | None], _PendingNote] = {}

        for msg in track:
            absolute_tick += int(msg.time)

            if msg.type == "track_name":
                track_name = msg.name or ""
                continue

            if msg.type == "program_change":
                channel_programs[int(msg.channel)] = int(msg.program)
                continue

            if msg.type == "note_on" and msg.velocity > 0:
                key = (int(msg.note), getattr(msg, "channel", None))
                instrument = _instrument_from_track(
                    track_name,
                    getattr(msg, "channel", None),
                    track_index,
                    channel_programs,
                )
                pending[key] = _PendingNote(
                    start_tick=absolute_tick,
                    velocity=int(msg.velocity),
                    instrument=instrument,
                )
                continue

            is_note_off = msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0)
            if not is_note_off:
                continue

            key = (int(msg.note), getattr(msg, "channel", None))
            start = pending.pop(key, None)
            if start is None:
                continue

            duration_ticks = max(1, absolute_tick - start.start_tick)
            beat_position = start.start_tick / midi.ticks_per_beat
            duration_beats = duration_ticks / midi.ticks_per_beat
            instrument = start.instrument

            notes.append(
                (
                    start.start_tick,
                    track_index,
                    ParsedNote(
                        instrument=instrument,
                        pitch=int(msg.note),
                        duration=duration_beats,
                        volume=start.velocity,
                        beat_position=beat_position,
                    ),
                )
            )

    notes.sort(key=lambda item: (item[0], item[1]))
    return [item[2] for item in notes]

