from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from mido import MidiFile

from app.models import ParsedNote


@dataclass(slots=True)
class _PendingNote:
    start_tick: int
    velocity: int


def _instrument_from_track(track_name: str, channel: int | None, track_index: int) -> str:
    lowered = track_name.lower()
    if "violin" in lowered:
        return "violin"
    if "piano" in lowered or "keys" in lowered:
        return "piano"
    if "drum" in lowered or "percussion" in lowered:
        return "drums"
    if "cello" in lowered or "bass" in lowered:
        return "cello"

    if channel == 9:
        return "drums"

    fallback = ("violin", "piano", "cello", "drums")
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
        pending: dict[tuple[int, int | None], _PendingNote] = {}

        for msg in track:
            absolute_tick += int(msg.time)

            if msg.type == "track_name":
                track_name = msg.name or ""
                continue

            if msg.type == "note_on" and msg.velocity > 0:
                key = (int(msg.note), getattr(msg, "channel", None))
                pending[key] = _PendingNote(start_tick=absolute_tick, velocity=int(msg.velocity))
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
            instrument = _instrument_from_track(
                track_name, getattr(msg, "channel", None), track_index
            )

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
