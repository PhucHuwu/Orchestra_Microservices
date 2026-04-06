"use client";

import type { ServiceToggleItem } from "@/lib/api/contracts";

type Props = {
  items: ServiceToggleItem[];
  pendingService: string | null;
  onToggle: (serviceName: string, enabled: boolean) => void;
};

export function ServiceToggleGrid({ items, pendingService, onToggle }: Props) {
  if (items.length === 0) {
    return <p className="text-sm text-[var(--text-muted)]">Không tìm thấy service nào có thể điều khiển.</p>;
  }

  return (
    <div className="grid gap-3 md:grid-cols-2">
      {items.map((item) => {
        const pending = pendingService === item.service_name;
        return (
          <div key={item.service_name} className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-3 text-sm">
            <div className="flex items-center justify-between gap-3">
              <p className="font-semibold text-[var(--text-strong)]">{item.service_name}</p>
              <span className="pill border-[var(--border)] bg-[var(--card-muted)]">{item.status}</span>
            </div>
            <p className="mt-1 text-xs text-[var(--text-muted)]">
              reachable={String(item.reachable)} running={String(item.worker_enabled ?? item.enabled)}
            </p>
            <div className="mt-3 flex gap-2">
              <button
                type="button"
                onClick={() => onToggle(item.service_name, true)}
                disabled={pending}
                className="rounded-lg bg-[var(--accent-strong)] px-3 py-1.5 text-xs font-semibold text-white disabled:opacity-60"
              >
                {pending && !item.enabled ? "Đang bắt đầu..." : "Start"}
              </button>
              <button
                type="button"
                onClick={() => onToggle(item.service_name, false)}
                disabled={pending}
                className="rounded-lg border border-[var(--border)] bg-[var(--card)] px-3 py-1.5 text-xs font-semibold disabled:opacity-60"
              >
                {pending && item.enabled ? "Đang dừng..." : "Stop"}
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}
