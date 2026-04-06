"use client";

import type { InteractionEdge, ServiceToggleItem } from "@/lib/api/contracts";

type Props = {
  socketStatus: "connected" | "disconnected" | "reconnecting";
  serviceControls: ServiceToggleItem[];
  interactions: InteractionEdge[];
  queueDepth: Record<string, number>;
  messageRate: Record<string, number>;
  consumerCount: Record<string, number>;
  pendingService: string | null;
};

type QueueInsight = {
  queue: string;
  depth: number;
  rate: number;
  consumers: number;
};

export function MicroserviceProofBoard({
  socketStatus,
  serviceControls,
  interactions,
  queueDepth,
  messageRate,
  consumerCount,
  pendingService
}: Props) {
  const totalServices = serviceControls.length;
  const reachableServices = serviceControls.filter((item) => item.reachable).length;
  const enabledServices = serviceControls.filter((item) => item.enabled).length;
  const independentlyControlled = serviceControls.filter((item) => item.service_name !== "dashboard-api").length;
  const activeEdges = interactions.filter((edge) => edge.depth > 0 || edge.message_rate > 0).length;
  const disabledServices = serviceControls.filter((item) => !item.enabled).map((item) => item.service_name);

  const topologyEdges = dedupeTopologyEdges(interactions);

  const queueInsights: QueueInsight[] = Object.keys(queueDepth)
    .filter((queue) => !queue.endsWith(".dlq"))
    .map((queue) => ({
      queue,
      depth: queueDepth[queue] ?? 0,
      rate: messageRate[queue] ?? 0,
      consumers: consumerCount[queue] ?? 0
    }))
    .sort((a, b) => b.rate - a.rate)
    .slice(0, 6);

  return (
    <div className="space-y-4">
      <div className="grid gap-3 md:grid-cols-5">
        <EvidenceCard label="Reachable Services" value={`${reachableServices}/${totalServices}`} hint="Service runtime đang online" />
        <EvidenceCard label="Enabled Services" value={`${enabledServices}/${totalServices}`} hint="Đang xử lý event" />
        <EvidenceCard label="Independent Control" value={String(independentlyControlled)} hint="Có thể bật/tắt từng service" />
        <EvidenceCard label="Event Edges" value={String(activeEdges)} hint="Luồng producer -> consumer qua queue" />
        <EvidenceCard label="Sync Stream" value={socketStatus} hint="Cập nhật realtime qua WebSocket" />
      </div>

      <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-3 text-sm">
        <p className="font-semibold text-[var(--text-strong)]">Live Control Mirror</p>
        <p className="mt-1 text-xs text-[var(--text-muted)]">
          Service đang tắt: {disabledServices.length > 0 ? disabledServices.join(", ") : "không có"}
        </p>
        {pendingService ? (
          <p className="mt-1 text-xs text-[var(--warning)]">Đang áp dụng thay đổi: {pendingService}</p>
        ) : (
          <p className="mt-1 text-xs text-[var(--text-muted)]">Không có thay đổi đang chờ.</p>
        )}
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-4">
          <h3 className="text-sm font-semibold text-[var(--text-strong)]">Service Topology (Live)</h3>
          <p className="mt-1 text-xs text-[var(--text-muted)]">
            Bằng chứng microservices: mỗi node là runtime deploy độc lập, liên kết qua queue.
          </p>
          <div className="mt-3 space-y-2 text-sm">
            {topologyEdges.slice(0, 8).map((edge) => (
              <div key={`${edge.from_service}-${edge.to_service}-${edge.queue}`} className="rounded-lg border border-[var(--border)] bg-[var(--card-muted)] px-3 py-2">
                <p className="font-medium text-[var(--text-strong)]">
                  {edge.from_service} -&gt; {edge.to_service}
                </p>
                <p className="text-xs text-[var(--text-muted)]">
                  queue={edge.queue} depth={edge.depth} consumers={edge.consumers} rate={edge.message_rate.toFixed(2)} msg/s
                </p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-4">
          <h3 className="text-sm font-semibold text-[var(--text-strong)]">Event-Driven Queue Watch</h3>
          <p className="mt-1 text-xs text-[var(--text-muted)]">
            Rate cao nghĩa là event đang chạy mạnh; depth cao nghĩa là queue đang bị tồn backlog.
          </p>
          <div className="mt-3 space-y-2 text-sm">
            {queueInsights.map((item) => {
              const state =
                item.consumers === 0 && (item.depth > 0 || item.rate > 0)
                  ? "blocked"
                  : item.depth > 200
                    ? "busy"
                    : item.consumers > 0
                      ? "healthy"
                      : "idle";
              const tone =
                state === "blocked"
                  ? "border-[var(--danger)] bg-[var(--danger-soft)]"
                  : state === "busy"
                    ? "border-[var(--warning)] bg-[var(--warning-soft)]"
                    : state === "idle"
                      ? "border-[var(--border)] bg-[var(--card)]"
                      : "border-[var(--border)] bg-[var(--card-muted)]";
              return (
                <div key={item.queue} className={`rounded-lg border px-3 py-2 ${tone}`}>
                  <p className="font-medium text-[var(--text-strong)]">{item.queue}</p>
                  <p className="text-xs text-[var(--text-muted)]">
                    rate={item.rate.toFixed(2)} msg/s depth={item.depth} consumers={item.consumers} trạng thái={state}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

function dedupeTopologyEdges(edges: InteractionEdge[]): InteractionEdge[] {
  const result: InteractionEdge[] = [];
  let instrumentOutputAdded = false;

  for (const edge of edges) {
    if (edge.queue === "instrument.output") {
      if (instrumentOutputAdded) {
        continue;
      }
      instrumentOutputAdded = true;
      result.push({
        ...edge,
        from_service: "instrument-services",
        to_service: "mixer"
      });
      continue;
    }
    result.push(edge);
  }

  return result;
}

function EvidenceCard({ label, value, hint }: { label: string; value: string; hint: string }) {
  return (
    <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-3">
      <p className="text-xs uppercase tracking-[0.08em] text-[var(--text-muted)]">{label}</p>
      <p className="mt-1 text-xl font-semibold text-[var(--text-strong)]">{value}</p>
      <p className="mt-1 text-xs text-[var(--text-muted)]">{hint}</p>
    </div>
  );
}
