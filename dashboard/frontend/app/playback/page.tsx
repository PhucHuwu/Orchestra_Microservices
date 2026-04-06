"use client";

import { useMutation } from "@tanstack/react-query";
import { useQuery } from "@tanstack/react-query";
import { useEffect } from "react";
import { useState } from "react";

import { DashboardShell } from "@/components/layout/dashboard-shell";
import { StatePanel } from "@/components/shared/state-panel";
import { PlaybackControlForm } from "@/features/playback/playback-control-form";
import { fetchScores, startPlayback, stopPlayback, uploadScore } from "@/lib/api/dashboard-api";
import { playbackFormSchema } from "@/features/playback/schema";
import { useSessionStore } from "@/stores/session-store";
import { useToastStore } from "@/stores/toast-store";

type FormState = {
  score_id: string;
  initial_bpm: number;
};

const initialState: FormState = {
  score_id: "",
  initial_bpm: 120
};

export default function PlaybackPage() {
  const [form, setForm] = useState<FormState>(initialState);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [validationMessage, setValidationMessage] = useState<string | null>(null);
  const { sessionId, status, setRunning, setStopped, setFailed } = useSessionStore();
  const pushToast = useToastStore((state) => state.push);

  const scoresQuery = useQuery({
    queryKey: ["scores"],
    queryFn: fetchScores,
    refetchInterval: 4000
  });

  const scores = scoresQuery.data ?? [];

  useEffect(() => {
    if (!form.score_id && scores.length > 0) {
      setForm((prev) => ({ ...prev, score_id: scores[0].id }));
    }
  }, [form.score_id, scores]);

  const startMutation = useMutation({
    mutationFn: startPlayback,
    onSuccess: (data) => {
      setRunning({ sessionId: data.session_id, bpm: form.initial_bpm });
      pushToast({ type: "success", title: "Playback đã bắt đầu", description: `Session ${data.session_id}` });
    },
    onError: (error: Error) => {
      setFailed();
      pushToast({ type: "error", title: "Bắt đầu playback thất bại", description: error.message });
    }
  });

  const stopMutation = useMutation({
    mutationFn: stopPlayback,
    onSuccess: () => {
      setStopped();
      pushToast({ type: "success", title: "Playback đã dừng" });
    },
    onError: (error: Error) => {
      pushToast({ type: "error", title: "Dừng playback thất bại", description: error.message });
    }
  });

  const uploadMutation = useMutation({
    mutationFn: uploadScore,
    onSuccess: (created) => {
      pushToast({ type: "success", title: "Tải file score thành công", description: created.name });
      setSelectedFile(null);
      setForm((prev) => ({ ...prev, score_id: created.id }));
      scoresQuery.refetch();
    },
    onError: (error: Error) => {
      pushToast({ type: "error", title: "Tải file thất bại", description: error.message });
    }
  });

  const onStart = () => {
    const parsed = playbackFormSchema.safeParse(form);
    if (!parsed.success) {
      const message = parsed.error.issues[0]?.message ?? "Dữ liệu đầu vào không hợp lệ";
      setValidationMessage(message);
      return;
    }
    setValidationMessage(null);
    startMutation.mutate(parsed.data);
  };

  const onUpload = () => {
    if (!selectedFile) {
      pushToast({ type: "info", title: "Hãy chọn file MIDI trước" });
      return;
    }
    uploadMutation.mutate(selectedFile);
  };

  const onStop = () => {
    if (!sessionId) {
      pushToast({ type: "info", title: "Không có session đang chạy", description: "Không có session để dừng." });
      return;
    }
    stopMutation.mutate({ session_id: sessionId });
  };

  return (
    <DashboardShell>
      <div className="grid gap-5 lg:grid-cols-[1.1fr,0.9fr]">
        <StatePanel title="Điều khiển Playback" description="Bật/Tắt session theo contract /api/v1/playback/*.">
          <PlaybackControlForm
            scoreId={form.score_id}
            bpm={form.initial_bpm}
            scores={scores.map((score) => ({ id: score.id, name: score.name }))}
            selectedFileName={selectedFile?.name ?? null}
            uploadPending={uploadMutation.isPending}
            validationMessage={validationMessage}
            startPending={startMutation.isPending}
            stopPending={stopMutation.isPending}
            canStop={Boolean(sessionId)}
            onScoreChange={(scoreId) => setForm((prev) => ({ ...prev, score_id: scoreId }))}
            onBpmChange={(bpm) => setForm((prev) => ({ ...prev, initial_bpm: bpm }))}
            onFileChange={(file) => setSelectedFile(file)}
            onUpload={onUpload}
            onStart={onStart}
            onStop={onStop}
          />
        </StatePanel>

        <StatePanel title="Trạng thái Session" description="Trạng thái runtime hiện tại cho demo và audio output.">
          <div className="space-y-2 text-sm">
            <p>
              <span className="text-[var(--text-muted)]">Trạng thái:</span> <strong>{status}</strong>
            </p>
            <p>
              <span className="text-[var(--text-muted)]">Session ID:</span> {sessionId ?? "-"}
            </p>
            <p>
              <span className="text-[var(--text-muted)]">Hành động bắt đầu:</span>{" "}
              {startMutation.isSuccess ? "success" : startMutation.isError ? "error" : "idle"}
            </p>
            <p>
              <span className="text-[var(--text-muted)]">Hành động dừng:</span>{" "}
              {stopMutation.isSuccess ? "success" : stopMutation.isError ? "error" : "idle"}
            </p>
            <p className="pt-2 text-[var(--text-muted)]">
              Audio player được ghim ở cuối màn hình và tiếp tục phát khi chuyển trang.
            </p>
          </div>
        </StatePanel>
      </div>
    </DashboardShell>
  );
}
