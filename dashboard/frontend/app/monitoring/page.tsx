"use client";

import { useQuery } from "@tanstack/react-query";
import { useMutation } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";

import { DashboardShell } from "@/components/layout/dashboard-shell";
import { InteractionFlowTable } from "@/components/monitoring/interaction-flow-table";
import { MetricLineChart } from "@/components/monitoring/metric-line-chart";
import { MicroserviceProofBoard } from "@/components/monitoring/microservice-proof-board";
import { ServiceToggleGrid } from "@/components/monitoring/service-toggle-grid";
import { StatePanel } from "@/components/shared/state-panel";
import {
  fetchMetricsOverview,
  fetchServiceControls,
  fetchServicesHealth,
  setServiceControl
} from "@/lib/api/dashboard-api";
import { MetricsWsClient } from "@/lib/ws/metrics-ws";
import { toTitle } from "@/lib/utils/format";
import { useMetricsStore } from "@/stores/metrics-store";
import { useSessionStore } from "@/stores/session-store";
import { useToastStore } from "@/stores/toast-store";

type Point = { name: string; value: number };

function makePoint(label: string, value: number) {
  return { name: label, value };
}

export default function MonitoringPage() {
  const { latest, socketStatus, setLatest, setSocketStatus } = useMetricsStore();
  const [queueSeries, setQueueSeries] = useState<Point[]>([]);
  const [rateSeries, setRateSeries] = useState<Point[]>([]);
  const [pendingService, setPendingService] = useState<string | null>(null);
  const [controlOverrides, setControlOverrides] = useState<Record<string, boolean>>({});
  const pushToast = useToastStore((state) => state.push);
  const bumpAudioToken = useSessionStore((state) => state.bumpAudioToken);

  const overviewQuery = useQuery({
    queryKey: ["metrics-overview"],
    queryFn: fetchMetricsOverview,
    refetchInterval: 10_000
  });

  const healthQuery = useQuery({
    queryKey: ["services-health"],
    queryFn: fetchServicesHealth,
    refetchInterval: 10_000
  });

  const controlQuery = useQuery({
    queryKey: ["services-control"],
    queryFn: fetchServiceControls,
    refetchInterval: 4000
  });

  const toggleMutation = useMutation({
    mutationFn: setServiceControl,
    onSuccess: (item) => {
      controlQuery.refetch();
      setControlOverrides((prev) => ({ ...prev, [item.service_name]: item.enabled }));
      bumpAudioToken();
      pushToast({
        type: "success",
        title: `${item.service_name} ${item.enabled ? "đã bật" : "đã tắt"}`
      });
    },
    onError: (error: Error) => {
      pushToast({ type: "error", title: "Toggle thất bại", description: error.message });
    },
    onSettled: () => {
      setPendingService(null);
    }
  });

  useEffect(() => {
    const client = new MetricsWsClient(
      (payload) => {
        setLatest(payload);

        const totalDepth = Object.values(payload.metrics.queue_depth).reduce((sum, current) => sum + current, 0);
        const totalRate = Object.values(payload.metrics.message_rate).reduce((sum, current) => sum + current, 0);
        const stamp = new Date(payload.ts).toLocaleTimeString();

        setQueueSeries((prev) => [...prev.slice(-14), makePoint(stamp, totalDepth)]);
        setRateSeries((prev) => [...prev.slice(-14), makePoint(stamp, Number(totalRate.toFixed(2)))]);
      },
      (status) => setSocketStatus(status)
    );

    client.connect();
    return () => client.dispose();
  }, [setLatest, setSocketStatus]);

  const overview = latest?.metrics ?? overviewQuery.data;
  const queueRows = useMemo(
    () => Object.entries(overview?.queue_depth ?? {}).sort(([a], [b]) => a.localeCompare(b)),
    [overview]
  );

  const healthRows = healthQuery.data ?? latest?.metrics.services ?? [];
  const interactions = latest?.metrics.interactions ?? [];
  const serviceControlsBase = controlQuery.data ?? latest?.metrics.toggles ?? [];
  const serviceControls = serviceControlsBase.map((item) => {
    const override = controlOverrides[item.service_name];
    if (override === undefined) {
      return item;
    }
    return {
      ...item,
      enabled: override,
      status: override ? "enabled" : "disabled",
      worker_enabled: override
    };
  });

  const onToggleService = (serviceName: string, enabled: boolean) => {
    setPendingService(serviceName);
    toggleMutation.mutate({ service_name: serviceName, enabled });
  };

  return (
    <DashboardShell>
      <div className="grid gap-5 xl:grid-cols-[1.2fr,0.8fr]">
        <div className="space-y-5">
          <StatePanel
            title="System Metrics"
            description="Queue depth, consumer count và message rate được cập nhật mỗi 1s qua WebSocket."
          >
            {overviewQuery.isLoading && !overview ? (
              <p className="text-sm text-[var(--text-muted)]">Đang tải metrics...</p>
            ) : null}

            {!overviewQuery.isLoading && queueRows.length === 0 ? (
              <p className="text-sm text-[var(--text-muted)]">Không có dữ liệu metrics.</p>
            ) : null}

            {overviewQuery.isError ? (
              <p className="rounded-xl border border-[var(--danger)] bg-[var(--danger-soft)] px-3 py-2 text-sm text-[var(--danger)]">
                Lỗi khi tải metrics overview.
              </p>
            ) : null}

            {queueRows.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="min-w-full text-sm">
                  <thead>
                    <tr className="text-left text-[var(--text-muted)]">
                      <th className="py-2">Queue</th>
                      <th className="py-2">Depth</th>
                      <th className="py-2">Consumers</th>
                      <th className="py-2">Rate</th>
                    </tr>
                  </thead>
                  <tbody>
                    {queueRows.map(([queue, depth]) => (
                      <tr key={queue} className="border-t border-[var(--border)]">
                        <td className="py-2">{queue}</td>
                        <td className="py-2">{depth}</td>
                        <td className="py-2">{overview?.consumer_count[queue] ?? 0}</td>
                        <td className="py-2">{(overview?.message_rate[queue] ?? 0).toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : null}
          </StatePanel>

          <StatePanel title="Realtime Charts" description="Biểu đồ xu hướng cho tổng queue depth và message rate.">
            {socketStatus !== "connected" && queueSeries.length === 0 ? (
              <p className="text-sm text-[var(--text-muted)]">Đang chờ realtime stream...</p>
            ) : (
              <div className="grid gap-4 lg:grid-cols-2">
                <MetricLineChart data={queueSeries} color="#0f766e" />
                <MetricLineChart data={rateSeries} color="#b45309" />
              </div>
            )}
          </StatePanel>

          <StatePanel
            title="Microservices Proof"
            description="Bằng chứng realtime cho thấy hệ thống này là microservices + event-driven + đồng bộ bằng queue."
          >
            <MicroserviceProofBoard
              socketStatus={socketStatus}
              serviceControls={serviceControls}
              pendingService={pendingService}
              interactions={
                interactions.length > 0
                  ? interactions
                  : Object.entries(overview?.queue_depth ?? {}).map(([queue]) => ({
                      from_service: "unknown",
                      to_service: "unknown",
                      queue,
                      depth: overview?.queue_depth[queue] ?? 0,
                      consumers: overview?.consumer_count[queue] ?? 0,
                      message_rate: overview?.message_rate[queue] ?? 0
                    }))
              }
              queueDepth={overview?.queue_depth ?? {}}
              messageRate={overview?.message_rate ?? {}}
              consumerCount={overview?.consumer_count ?? {}}
            />
          </StatePanel>

          <StatePanel
            title="Interaction Flow"
            description="Tương tác queue realtime giữa các service (producer -> consumer)."
          >
            <InteractionFlowTable
              edges={
                interactions.length > 0
                  ? interactions
                  : Object.entries(overview?.queue_depth ?? {}).map(([queue]) => ({
                      from_service: "unknown",
                      to_service: "unknown",
                      queue,
                      depth: overview?.queue_depth[queue] ?? 0,
                      consumers: overview?.consumer_count[queue] ?? 0,
                      message_rate: overview?.message_rate[queue] ?? 0
                    }))
              }
            />
          </StatePanel>
        </div>

        <div className="space-y-5">
          <StatePanel title="Trạng thái Socket" description="Trạng thái kết nối hiện tại của WS /ws/metrics.">
            <p className="text-sm">
              <span className="pill border-[var(--border)] bg-[var(--card)]">{socketStatus}</span>
            </p>
          </StatePanel>

          <StatePanel title="Service Health" description="Tổng quan trạng thái service từ /api/v1/services/health.">
            {healthQuery.isLoading && healthRows.length === 0 ? (
              <p className="text-sm text-[var(--text-muted)]">Đang tải service health...</p>
            ) : null}
            {healthQuery.isError ? (
              <p className="rounded-xl border border-[var(--danger)] bg-[var(--danger-soft)] px-3 py-2 text-sm text-[var(--danger)]">
                Lỗi khi tải service health.
              </p>
            ) : null}
            {healthRows.length === 0 && !healthQuery.isLoading ? (
              <p className="text-sm text-[var(--text-muted)]">Không có snapshot service health.</p>
            ) : null}
            <div className="space-y-2">
              {healthRows.map((item) => (
                <div key={`${item.service_name}-${item.captured_at ?? "now"}`} className="rounded-xl border border-[var(--border)] p-3 text-sm">
                  <p className="font-semibold text-[var(--text-strong)]">{toTitle(item.service_name)}</p>
                  <p className="text-xs text-[var(--text-muted)]">
                    status={item.status} latency={item.latency_ms ?? "-"}ms queue={item.queue_depth} consumers={item.consumer_count}
                  </p>
                </div>
              ))}
            </div>
          </StatePanel>

          <StatePanel
            title="Điều khiển Service"
            description="Bật/tắt từng worker service và quan sát tác động lên queue interaction theo realtime."
          >
            <ServiceToggleGrid
              items={serviceControls}
              pendingService={pendingService}
              onToggle={onToggleService}
            />
          </StatePanel>
        </div>
      </div>
    </DashboardShell>
  );
}
