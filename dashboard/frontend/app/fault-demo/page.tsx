"use client";

import { useState } from "react";

import { DashboardShell } from "@/components/layout/dashboard-shell";
import { StatePanel } from "@/components/shared/state-panel";
import { useSessionStore } from "@/stores/session-store";
import { useToastStore } from "@/stores/toast-store";

type Scenario = {
  id: "consumer-lag" | "service-crash-recovery" | "competing-consumers";
  label: string;
  description: string;
};

type TimelineItem = {
  id: string;
  ts: string;
  scenario: string;
  action: "run" | "cleanup";
};

const scenarios: Scenario[] = [
  {
    id: "consumer-lag",
    label: "Consumer lag",
    description: "Giả lập queue bị dồn do consumer xử lý chậm."
  },
  {
    id: "service-crash-recovery",
    label: "Crash & recovery",
    description: "Giả lập service bị crash và khôi phục lại."
  },
  {
    id: "competing-consumers",
    label: "Scale consumer",
    description: "Giả lập competing consumers trên cùng một queue."
  },
];

const BACKEND_FAULT_ENDPOINT = process.env.NEXT_PUBLIC_FAULT_API_BASE_URL;

async function callFaultEndpoint(action: "run" | "cleanup", scenario: Scenario["id"]) {
  if (!BACKEND_FAULT_ENDPOINT) {
    return { simulated: true };
  }

  const response = await fetch(`${BACKEND_FAULT_ENDPOINT}/api/v1/fault/${action}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ scenario })
  });

  if (!response.ok) {
    throw new Error(`Fault API failed (${response.status})`);
  }

  return response.json();
}

export default function FaultDemoPage() {
  const [timeline, setTimeline] = useState<TimelineItem[]>([]);
  const [pendingKey, setPendingKey] = useState<string | null>(null);
  const pushToast = useToastStore((state) => state.push);
  const bumpAudioToken = useSessionStore((state) => state.bumpAudioToken);

  const trigger = async (scenario: Scenario, action: "run" | "cleanup") => {
    const key = `${action}-${scenario.id}`;
    setPendingKey(key);
    try {
      await callFaultEndpoint(action, scenario.id);
      const item: TimelineItem = {
        id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
        ts: new Date().toISOString(),
        scenario: scenario.label,
        action
      };
      setTimeline((prev) => [item, ...prev]);
      bumpAudioToken();
      pushToast({
        type: "success",
        title: `${action === "run" ? "Đã kích hoạt" : "Đã cleanup"} ${scenario.label}`
      });
    } catch (error) {
      pushToast({ type: "error", title: "Fault scenario thất bại", description: (error as Error).message });
    } finally {
      setPendingKey(null);
    }
  };

  return (
    <DashboardShell>
      <div className="grid gap-5 lg:grid-cols-[1.1fr,0.9fr]">
          <StatePanel
            title="Các Fault Scenario"
            description="Preset theo runbook: consumer lag, crash/recovery, scale consumer."
          >
          <div className="space-y-3">
            {scenarios.map((scenario) => (
              <div key={scenario.id} className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-4">
                <p className="font-semibold text-[var(--text-strong)]">{scenario.label}</p>
                <p className="mt-1 text-sm text-[var(--text-muted)]">{scenario.description}</p>
                <div className="mt-3 flex gap-2">
                  <button
                    type="button"
                    onClick={() => void trigger(scenario, "run")}
                    disabled={pendingKey !== null}
                    className="rounded-xl bg-[var(--accent-strong)] px-3 py-2 text-xs font-semibold text-white disabled:opacity-60"
                  >
                    {pendingKey === `run-${scenario.id}` ? "Đang chạy..." : "Run"}
                  </button>
                  <button
                    type="button"
                    onClick={() => void trigger(scenario, "cleanup")}
                    disabled={pendingKey !== null}
                    className="rounded-xl border border-[var(--border)] bg-[var(--card)] px-3 py-2 text-xs font-semibold text-[var(--text-base)] disabled:opacity-60"
                  >
                    {pendingKey === `cleanup-${scenario.id}` ? "Đang cleanup..." : "Cleanup"}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </StatePanel>

        <StatePanel title="Event Timeline" description="Các sự kiện Fault trigger sắp xếp từ mới nhất đến cũ nhất.">
          {timeline.length === 0 ? (
            <p className="text-sm text-[var(--text-muted)]">Chưa có sự kiện nào.</p>
          ) : (
            <ol className="space-y-2">
              {timeline.map((item) => (
                <li key={item.id} className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-3 text-sm">
                  <p className="font-medium text-[var(--text-strong)]">{item.scenario}</p>
                  <p className="text-xs text-[var(--text-muted)]">
                    action={item.action} at {new Date(item.ts).toLocaleString()}
                  </p>
                </li>
              ))}
            </ol>
          )}
        </StatePanel>
      </div>
    </DashboardShell>
  );
}
