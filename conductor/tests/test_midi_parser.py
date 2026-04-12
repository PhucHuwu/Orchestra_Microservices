from pathlib import Path

from mido import Message, MetaMessage, MidiFile, MidiTrack

from app.midi_parser import parse_midi_file


def _write_sample_midi(path: Path) -> None:
    midi = MidiFile(ticks_per_beat=480)

    violin_track = MidiTrack()
    violin_track.append(MetaMessage("track_name", name="Violin", time=0))
    violin_track.append(Message("note_on", note=64, velocity=96, channel=0, time=0))
    violin_track.append(Message("note_off", note=64, velocity=0, channel=0, time=480))
    midi.tracks.append(violin_track)

    drums_track = MidiTrack()
    drums_track.append(MetaMessage("track_name", name="Drums", time=0))
    drums_track.append(Message("note_on", note=36, velocity=110, channel=9, time=0))
    drums_track.append(Message("note_off", note=36, velocity=0, channel=9, time=240))
    midi.tracks.append(drums_track)

    midi.save(str(path))


def test_parse_midi_file_maps_instruments_and_notes(tmp_path: Path) -> None:
    score_dir = tmp_path / "scores"
    score_dir.mkdir(parents=True)
    midi_path = score_dir / "sample.mid"
    _write_sample_midi(midi_path)

    notes = parse_midi_file("sample.mid", score_dir=str(score_dir))

    assert len(notes) == 2
    assert notes[0].instrument == "guitar"
    assert notes[0].pitch == 64
    assert notes[0].duration == 1.0
    assert notes[0].volume == 96
    assert notes[1].instrument == "drums"
    assert notes[1].pitch == 36
    assert notes[1].duration == 0.5
