from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path

from mido import MetaMessage, MidiFile, MidiTrack

LOGGER = logging.getLogger(__name__)
TRACK_INSTRUMENTS = ("violin", "piano", "drums", "cello")


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
            "violin": True,
            "piano": True,
            "drums": True,
            "cello": True,
        }
        self._source_midi: Path | None = None

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

    def render_midi_file(self, midi_path: str) -> Path:
        self._source_midi = Path(midi_path).resolve()
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

        for track_index, track in enumerate(source_midi.tracks):
            out_track = MidiTrack()
            muted_accumulated_ticks = 0
            track_instrument = self._infer_track_instrument(track_index, track)

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

        return output

    def _infer_track_instrument(self, track_index: int, track: MidiTrack) -> str | None:
        has_notes = any(msg.type in {"note_on", "note_off"} for msg in track)
        if not has_notes:
            return None
        return TRACK_INSTRUMENTS[track_index % len(TRACK_INSTRUMENTS)]

    def _infer_message_instrument(self, msg, track_instrument: str | None) -> str | None:
        if hasattr(msg, "channel") and msg.channel == 9:
            return "drums"
        return track_instrument
