"use client";

import { useMutation } from "@tanstack/react-query";
import { useState } from "react";

import { DashboardShell } from "@/components/layout/dashboard-shell";
import { StatePanel } from "@/components/shared/state-panel";
import { PlaybackControlForm } from "@/features/playback/playback-control-form";
import { startPlayback, stopPlayback } from "@/lib/api/dashboard-api";
import { SCORE_OPTIONS } from "@/lib/constants/scores";
import { playbackFormSchema } from "@/features/playback/schema";
import { useSessionStore } from "@/stores/session-store";
import { useToastStore } from "@/stores/toast-store";

type FormState = {
  score_id: string;
  initial_bpm: number;
};

const initialState: FormState = {
  score_id: SCORE_OPTIONS[0]?.id ?? "",
  initial_bpm: 120
};

export default function PlaybackPage() {
  const [form, setForm] = useState<FormState>(initialState);
  const [validationMessage, setValidationMessage] = useState<string | null>(null);
  const { sessionId, status, setRunning, setStopped, setFailed } = useSessionStore();
  const pushToast = useToastStore((state) => state.push);

  const startMutation = useMutation({
    mutationFn: startPlayback,
    onSuccess: (data) => {
      setRunning({ sessionId: data.session_id, bpm: form.initial_bpm });
      pushToast({ type: "success", title: "Playback started", description: `Session ${data.session_id}` });
    },
    onError: (error: Error) => {
      setFailed();
      pushToast({ type: "error", title: "Start playback failed", description: error.message });
    }
  });

  const stopMutation = useMutation({
    mutationFn: stopPlayback,
    onSuccess: () => {
      setStopped();
      pushToast({ type: "success", title: "Playback stopped" });
    },
    onError: (error: Error) => {
      pushToast({ type: "error", title: "Stop playback failed", description: error.message });
    }
  });

  const onStart = () => {
    const parsed = playbackFormSchema.safeParse(form);
    if (!parsed.success) {
      const message = parsed.error.issues[0]?.message ?? "Invalid input";
      setValidationMessage(message);
      return;
    }
    setValidationMessage(null);
    startMutation.mutate(parsed.data);
  };

  const onStop = () => {
    if (!sessionId) {
      pushToast({ type: "info", title: "No running session", description: "No session to stop." });
      return;
    }
    stopMutation.mutate({ session_id: sessionId });
  };

  return (
    <DashboardShell>
      <div className="grid gap-5 lg:grid-cols-[1.1fr,0.9fr]">
        <StatePanel title="Playback Control" description="Start/Stop session theo contract /api/v1/playback/*.">
          <PlaybackControlForm
            scoreId={form.score_id}
            bpm={form.initial_bpm}
            validationMessage={validationMessage}
            startPending={startMutation.isPending}
            stopPending={stopMutation.isPending}
            canStop={Boolean(sessionId)}
            onScoreChange={(scoreId) => setForm((prev) => ({ ...prev, score_id: scoreId }))}
            onBpmChange={(bpm) => setForm((prev) => ({ ...prev, initial_bpm: bpm }))}
            onStart={onStart}
            onStop={onStop}
          />
        </StatePanel>

        <StatePanel title="Session Status" description="Current runtime status for the demo.">
          <div className="space-y-2 text-sm">
            <p>
              <span className="text-[var(--text-muted)]">Status:</span> <strong>{status}</strong>
            </p>
            <p>
              <span className="text-[var(--text-muted)]">Session ID:</span> {sessionId ?? "-"}
            </p>
            <p>
              <span className="text-[var(--text-muted)]">Start action:</span>{" "}
              {startMutation.isSuccess ? "success" : startMutation.isError ? "error" : "idle"}
            </p>
            <p>
              <span className="text-[var(--text-muted)]">Stop action:</span>{" "}
              {stopMutation.isSuccess ? "success" : stopMutation.isError ? "error" : "idle"}
            </p>
          </div>
        </StatePanel>
      </div>
    </DashboardShell>
  );
}
