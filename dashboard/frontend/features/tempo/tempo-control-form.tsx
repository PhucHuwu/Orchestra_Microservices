import React from "react";

type TempoControlFormProps = {
  value: number;
  disabled: boolean;
  validationMessage: string | null;
  pending: boolean;
  onValueChange: (value: number) => void;
  onApply: () => void;
};

export function TempoControlForm(props: TempoControlFormProps) {
  return (
    <div className="space-y-4">
      <label className="block text-sm font-medium text-[var(--text-base)]">
        Thanh trượt BPM
        <input
          type="range"
          min={20}
          max={300}
          value={props.value}
          onChange={(event) => props.onValueChange(Number(event.target.value))}
          className="mt-2 w-full"
        />
      </label>

      <label className="block text-sm font-medium text-[var(--text-base)]">
        Giá trị BPM
        <input
          type="number"
          min={20}
          max={300}
          value={props.value}
          onChange={(event) => props.onValueChange(Number(event.target.value))}
          className="mt-1 w-full rounded-xl border border-[var(--border)] bg-[var(--card)] px-3 py-2"
        />
      </label>

      {props.validationMessage ? (
        <p className="rounded-xl border border-[var(--danger)] bg-[var(--danger-soft)] px-3 py-2 text-sm text-[var(--danger)]">
          {props.validationMessage}
        </p>
      ) : null}

      <button
        type="button"
        onClick={props.onApply}
        disabled={props.disabled || props.pending}
        className="rounded-xl bg-[var(--accent-strong)] px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
      >
          {props.pending ? "Đang áp dụng..." : "Apply BPM"}
      </button>
    </div>
  );
}
