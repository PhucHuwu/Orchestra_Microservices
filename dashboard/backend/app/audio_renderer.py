from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path

from mido import MetaMessage, MidiFile, MidiTrack, bpm2tempo

LOGGER = logging.getLogger(__name__)
TRACK_INSTRUMENTS = ("guitar", "oboe", "drums", "bass")


class PlaybackAudioRenderer:
    def __init__(
        self,
        sample_rate: int,
        output_dir: str,
        soundfont_path: str,
        rabbitmq_url: str,
        exchange_name: str,
        output_queue: str,
    ) -> None:
        self._sample_rate = sample_rate
        self._soundfont_path = Path(soundfont_path)
        self._output_dir = Path(output_dir).resolve()
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._latest_file = self._output_dir / "latest.wav"
        self._working_midi = self._output_dir / "latest_render.mid"

        self._enabled = {
            "guitar": True,
            "oboe": True,
            "drums": True,
            "bass": True,
        }
        self._source_midi: Path | None = None
        self._current_bpm = 120

        _ = rabbitmq_url
        _ = exchange_name
        _ = output_queue

    @property
    def latest_file_path(self) -> Path:
        return self._latest_file

    def start(self) -> None:
        return

    def stop(self) -> None:
        return

    def reset_session(self) -> None:
        if self._latest_file.exists():
            self._latest_file.unlink()

    def set_instrument_enabled(self, instrument: str, enabled: bool) -> None:
        key = instrument.strip().lower()
        if key in self._enabled:
            self._enabled[key] = enabled
            self.rerender_current()

    def render_midi_file(self, midi_path: str, bpm: int | None = None) -> Path:
        self._source_midi = Path(midi_path).resolve()
        if bpm is not None:
            self._current_bpm = bpm
        if not self._source_midi.exists():
            raise FileNotFoundError(f"MIDI file not found: {self._source_midi}")
        if not self._soundfont_path.exists():
            raise FileNotFoundError(f"SoundFont file not found: {self._soundfont_path}")

        self._render_current_state()
        return self._latest_file

    def rerender_current(self) -> Path | None:
        if self._source_midi is None:
            return None
        self._render_current_state()
        return self._latest_file

    def set_tempo(self, bpm: int) -> None:
        self._current_bpm = max(20, min(300, int(bpm)))
        self.rerender_current()

    def _render_current_state(self) -> None:
        assert self._source_midi is not None
        filtered = self._build_filtered_midi(self._source_midi)
        filtered.save(str(self._working_midi))

        temp_wav = self._output_dir / "latest.tmp.wav"
        command = [
            "fluidsynth",
            "-ni",
            str(self._soundfont_path),
            str(self._working_midi),
            "-F",
            str(temp_wav),
            "-r",
            str(self._sample_rate),
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise RuntimeError(f"fluidsynth failed: {result.stderr[-500:]}")
        if not temp_wav.exists() or temp_wav.stat().st_size == 0:
            raise RuntimeError("Rendered WAV is empty")
        os.replace(temp_wav, self._latest_file)

    def _build_filtered_midi(self, source: Path) -> MidiFile:
        source_midi = MidiFile(str(source))
        output = MidiFile(ticks_per_beat=source_midi.ticks_per_beat)

        if not any(self._enabled.values()):
            return MidiFile(ticks_per_beat=source_midi.ticks_per_beat)

        instrument_track_index = 0
        for track in source_midi.tracks:
            out_track = MidiTrack()
            muted_accumulated_ticks = 0
            track_instrument = self._infer_track_instrument(track)
            if track_instrument is None and any(msg.type in {"note_on", "note_off"} for msg in track):
                track_instrument = TRACK_INSTRUMENTS[instrument_track_index % len(TRACK_INSTRUMENTS)]
                instrument_track_index += 1

            preserve_all = track_instrument is None
            for msg in track:
                if preserve_all:
                    msg_copy = msg.copy(time=int(msg.time) + muted_accumulated_ticks)
                    muted_accumulated_ticks = 0
                    out_track.append(msg_copy)
                    continue

                instrument = self._infer_message_instrument(msg, track_instrument)
                if instrument is not None and not self._enabled.get(instrument, True):
                    muted_accumulated_ticks += int(msg.time)
                    continue

                msg_copy = msg.copy(time=int(msg.time) + muted_accumulated_ticks)
                muted_accumulated_ticks = 0
                out_track.append(msg_copy)

            if len(out_track) == 0:
                out_track.append(MetaMessage("end_of_track", time=0))
            output.tracks.append(out_track)

        self._apply_tempo_override(output)

        return output

    def _apply_tempo_override(self, midi: MidiFile) -> None:
        if len(midi.tracks) == 0:
            first = MidiTrack()
            first.append(MetaMessage("set_tempo", tempo=bpm2tempo(self._current_bpm), time=0))
            first.append(MetaMessage("end_of_track", time=0))
            midi.tracks.append(first)
            return

        for index, track in enumerate(midi.tracks):
            rebuilt = MidiTrack()
            carry_ticks = 0
            for msg in track:
                if msg.type == "set_tempo":
                    carry_ticks += int(msg.time)
                    continue
                rebuilt.append(msg.copy(time=int(msg.time) + carry_ticks))
                carry_ticks = 0
            if len(rebuilt) == 0:
                rebuilt.append(MetaMessage("end_of_track", time=0))
            midi.tracks[index] = rebuilt

        midi.tracks[0].insert(0, MetaMessage("set_tempo", tempo=bpm2tempo(self._current_bpm), time=0))

    def _infer_track_instrument(self, track: MidiTrack) -> str | None:
        track_name = ""
        for event in track:
            if event.type == "track_name":
                track_name = (event.name or "").lower()
                break

        if "guitar" in track_name or "violin" in track_name:
            return "guitar"
        if (
            "oboe" in track_name
            or "piano" in track_name
            or "keys" in track_name
            or "right hand" in track_name
            or "left hand" in track_name
        ):
            return "oboe"
        if "bass" in track_name or "cello" in track_name:
            return "bass"
        if "drum" in track_name or "perc" in track_name:
            return "drums"

        for event in track:
            if event.type == "program_change":
                program = int(event.program)
                if 0 <= program <= 7:
                    return "oboe"
                if 40 <= program <= 41:
                    return "guitar"
                if 42 <= program <= 43:
                    return "bass"

        for event in track:
            if hasattr(event, "channel") and event.channel == 9:
                return "drums"
        return None

    def _infer_message_instrument(self, msg, track_instrument: str | None) -> str | None:
        if hasattr(msg, "channel") and msg.channel == 9:
            return "drums"
        return track_instrument

