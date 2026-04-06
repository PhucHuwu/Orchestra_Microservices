import Link from "next/link";

import { DashboardShell } from "@/components/layout/dashboard-shell";

const modules = [
  {
    title: "Playback",
    href: "/playback",
    description: "Start/stop session, select MIDI score, track session status."
  },
  {
    title: "Tempo",
    href: "/tempo",
    description: "Adjust BPM in realtime with slider/input and confirm update time."
  },
  {
    title: "Monitoring",
    href: "/monitoring",
    description: "Monitor queue depth, consumers, message rate, health, and latency."
  },
  {
    title: "Fault Demo",
    href: "/fault-demo",
    description: "Trigger fault scenarios and track event timeline."
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
            <p className="mt-5 text-sm font-medium text-[var(--accent-strong)]">Open screen -&gt;</p>
          </Link>
        ))}
      </section>
    </DashboardShell>
  );
}
