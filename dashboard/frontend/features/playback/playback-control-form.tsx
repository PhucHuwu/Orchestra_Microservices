import React from "react";

type ScoreItem = {
  id: string;
  name: string;
};

type PlaybackControlFormProps = {
  scoreId: string;
  bpm: number;
  scores: ScoreItem[];
  selectedFileName: string | null;
  uploadPending: boolean;
  validationMessage: string | null;
  startPending: boolean;
  stopPending: boolean;
  canStop: boolean;
  onScoreChange: (scoreId: string) => void;
  onBpmChange: (bpm: number) => void;
  onFileChange: (file: File | null) => void;
  onUpload: () => void;
  onStart: () => void;
  onStop: () => void;
};

export function PlaybackControlForm(props: PlaybackControlFormProps) {
  return (
    <div className="space-y-4">
      <label className="block text-sm font-medium text-[var(--text-base)]">
        Score
        <select
          value={props.scoreId}
          onChange={(event) => props.onScoreChange(event.target.value)}
          className="mt-1 w-full rounded-xl border border-[var(--border)] bg-[var(--card)] px-3 py-2"
        >
          {props.scores.map((score) => (
            <option key={score.id} value={score.id}>
              {score.name}
            </option>
          ))}
        </select>
      </label>

      <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-3">
        <label className="block text-sm font-medium text-[var(--text-base)]">
          Upload MIDI (.mid)
          <input
            type="file"
            accept=".mid,audio/midi,audio/x-midi"
            onChange={(event) => props.onFileChange(event.target.files?.[0] ?? null)}
            className="mt-2 block w-full text-sm"
          />
        </label>
        <div className="mt-2 flex items-center justify-between gap-3 text-sm">
          <span className="truncate text-[var(--text-muted)]">{props.selectedFileName ?? "No file selected"}</span>
          <button
            type="button"
            onClick={props.onUpload}
            disabled={!props.selectedFileName || props.uploadPending}
            className="rounded-xl border border-[var(--border)] bg-[var(--card-muted)] px-3 py-2 font-semibold disabled:opacity-60"
          >
            {props.uploadPending ? "Uploading..." : "Upload"}
          </button>
        </div>
      </div>

      <label className="block text-sm font-medium text-[var(--text-base)]">
        Initial BPM
        <input
          type="number"
          min={20}
          max={300}
          value={props.bpm}
          onChange={(event) => props.onBpmChange(Number(event.target.value))}
          className="mt-1 w-full rounded-xl border border-[var(--border)] bg-[var(--card)] px-3 py-2"
        />
      </label>

      {props.validationMessage ? (
        <p className="rounded-xl border border-[var(--danger)] bg-[var(--danger-soft)] px-3 py-2 text-sm text-[var(--danger)]">
          {props.validationMessage}
        </p>
      ) : null}

      <div className="flex flex-wrap gap-3">
        <button
          type="button"
          onClick={props.onStart}
          disabled={props.startPending}
          className="rounded-xl bg-[var(--accent-strong)] px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
        >
          {props.startPending ? "Starting..." : "Start"}
        </button>
        <button
          type="button"
          onClick={props.onStop}
          disabled={props.stopPending || !props.canStop}
          className="rounded-xl border border-[var(--border)] bg-[var(--card)] px-4 py-2 text-sm font-semibold text-[var(--text-base)] disabled:opacity-60"
        >
          {props.stopPending ? "Stopping..." : "Stop"}
        </button>
      </div>
    </div>
  );
}
