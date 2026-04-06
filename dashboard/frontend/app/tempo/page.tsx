"use client";

import { useMutation } from "@tanstack/react-query";
import { useMemo, useState } from "react";

import { DashboardShell } from "@/components/layout/dashboard-shell";
import { StatePanel } from "@/components/shared/state-panel";
import { TempoControlForm } from "@/features/tempo/tempo-control-form";
import { tempoFormSchema } from "@/features/tempo/schema";
import { applyTempo } from "@/lib/api/dashboard-api";
import { formatDateTime } from "@/lib/utils/format";
import { useSessionStore } from "@/stores/session-store";
import { useToastStore } from "@/stores/toast-store";

export default function TempoPage() {
  const { sessionId, status, currentBpm, tempoUpdatedAt, setTempo } = useSessionStore();
  const pushToast = useToastStore((state) => state.push);
  const [value, setValue] = useState<number>(currentBpm ?? 120);
  const [validationMessage, setValidationMessage] = useState<string | null>(null);

  const disabled = status !== "running" || !sessionId;

  const mutation = useMutation({
    mutationFn: applyTempo,
    onSuccess: () => {
      setTempo({ bpm: value, updatedAt: new Date().toISOString() });
      pushToast({
        type: "success",
        title: "Tempo updated",
        description: `BPM ${value} command sent.`
      });
    },
    onError: (error: Error) => {
      pushToast({ type: "error", title: "Apply BPM failed", description: error.message });
    }
  });

  const effectiveBpm = useMemo(() => currentBpm ?? value, [currentBpm, value]);

  const onApply = () => {
    const parsed = tempoFormSchema.safeParse({ new_bpm: value });
    if (!parsed.success) {
      setValidationMessage(parsed.error.issues[0]?.message ?? "Invalid BPM value");
      return;
    }

    if (disabled || !sessionId) {
      pushToast({
        type: "info",
        title: "Session not running",
        description: "Start playback before sending tempo command."
      });
      return;
    }

    setValidationMessage(null);
    mutation.mutate({ session_id: sessionId, new_bpm: parsed.data.new_bpm });
  };

  return (
    <DashboardShell>
      <div className="grid gap-5 lg:grid-cols-[1.1fr,0.9fr]">
        <StatePanel title="Realtime Tempo" description="Adjust BPM via POST /api/v1/tempo.">
          <div className="space-y-4">
            <TempoControlForm
              value={value}
              disabled={disabled}
              validationMessage={validationMessage}
              pending={mutation.isPending}
              onValueChange={setValue}
              onApply={onApply}
            />

            {disabled ? (
              <p className="rounded-xl border border-[var(--warning)] bg-[var(--warning-soft)] px-3 py-2 text-sm text-[var(--warning)]">
                Session is not running. Start playback before sending tempo command.
              </p>
            ) : null}
          </div>
        </StatePanel>

        <StatePanel title="Tempo State" description="Current BPM and latest update timestamp.">
          <div className="space-y-2 text-sm">
            <p>
              <span className="text-[var(--text-muted)]">Session:</span> {sessionId ?? "-"}
            </p>
            <p>
              <span className="text-[var(--text-muted)]">Current BPM:</span> <strong>{effectiveBpm}</strong>
            </p>
            <p>
              <span className="text-[var(--text-muted)]">Last Updated:</span> {formatDateTime(tempoUpdatedAt)}
            </p>
            <p>
              <span className="text-[var(--text-muted)]">Mutation:</span>{" "}
              {mutation.isSuccess ? "success" : mutation.isError ? "error" : "idle"}
            </p>
          </div>
        </StatePanel>
      </div>
    </DashboardShell>
  );
}
