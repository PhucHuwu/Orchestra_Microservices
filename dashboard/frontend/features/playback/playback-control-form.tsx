import React from "react";

import { SCORE_OPTIONS } from "@/lib/constants/scores";

type PlaybackControlFormProps = {
  scoreId: string;
  bpm: number;
  validationMessage: string | null;
  startPending: boolean;
  stopPending: boolean;
  canStop: boolean;
  onScoreChange: (scoreId: string) => void;
  onBpmChange: (bpm: number) => void;
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
          {SCORE_OPTIONS.map((score) => (
            <option key={score.id} value={score.id}>
              {score.label}
            </option>
          ))}
        </select>
      </label>

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
