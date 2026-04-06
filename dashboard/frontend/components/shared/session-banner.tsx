"use client";

import { useSessionStore } from "@/stores/session-store";

function statusTone(status: "running" | "stopped" | "failed") {
  if (status === "running") {
    return "bg-[var(--accent-soft)] text-[var(--accent-strong)] border-[var(--accent-strong)]";
  }

  if (status === "failed") {
    return "bg-[var(--danger-soft)] text-[var(--danger)] border-[var(--danger)]";
  }

  return "bg-[var(--card)] text-[var(--text-muted)] border-[var(--border)]";
}

export function SessionBanner() {
  const { sessionId, status, currentBpm, tempoUpdatedAt } = useSessionStore();

  return (
    <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] px-4 py-3 text-sm">
      <div className="flex items-center gap-2">
        <span className={`pill ${statusTone(status)}`}>Session {status}</span>
        <span className="text-xs text-[var(--text-muted)]">{sessionId ?? "Chưa có session đang chạy"}</span>
      </div>
      <p className="mt-2 text-xs text-[var(--text-muted)]">
        BPM: {currentBpm ?? "-"} | Lần cập nhật tempo gần nhất: {tempoUpdatedAt ? new Date(tempoUpdatedAt).toLocaleTimeString() : "-"}
      </p>
    </div>
  );
}
