import Link from "next/link";

import { DashboardShell } from "@/components/layout/dashboard-shell";

const modules = [
  {
    title: "Playback",
    href: "/playback",
    description: "Start/stop session, chọn score MIDI, theo dõi trạng thái phiên."
  },
  {
    title: "Tempo",
    href: "/tempo",
    description: "Điều chỉnh BPM realtime bằng slider/input và xác nhận thời điểm cập nhật."
  },
  {
    title: "Monitoring",
    href: "/monitoring",
    description: "Giám sát queue depth, consumer, message rate, health và latency tổng quan."
  },
  {
    title: "Fault Demo",
    href: "/fault-demo",
    description: "Kích hoạt kịch bản lỗi và theo dõi timeline sự kiện demo."
  }
];

export default function HomePage() {
  return (
    <DashboardShell>
      <section className="grid gap-5 sm:grid-cols-2">
        {modules.map((module) => (
          <Link
            key={module.href}
            href={module.href}
            className="card-surface group block rounded-2xl p-6 transition hover:-translate-y-0.5"
          >
            <p className="text-xs uppercase tracking-[0.2em] text-[var(--text-muted)]">Screen</p>
            <h2 className="mt-2 font-heading text-3xl text-[var(--text-strong)]">{module.title}</h2>
            <p className="mt-3 text-sm text-[var(--text-base)]">{module.description}</p>
            <p className="mt-5 text-sm font-medium text-[var(--accent-strong)]">Open screen -></p>
          </Link>
        ))}
      </section>
    </DashboardShell>
  );
}
