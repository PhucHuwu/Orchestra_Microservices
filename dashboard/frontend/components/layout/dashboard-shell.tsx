"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ReactNode } from "react";

import { SessionBanner } from "@/components/shared/session-banner";
import { ToastViewport } from "@/components/shared/toast-viewport";

const navItems = [
  { href: "/playback", label: "Phát nhạc" },
  { href: "/tempo", label: "Tempo" },
  { href: "/monitoring", label: "Giám sát" },
  { href: "/fault-demo", label: "Fault Demo" }
];

export function DashboardShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();

  return (
    <main className="mx-auto min-h-screen w-full max-w-7xl px-4 py-6 md:px-8">
      <header className="fade-in rounded-2xl border border-[var(--border)] bg-[color:var(--card-muted)]/80 p-5">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <Link href="/" className="text-xs uppercase tracking-[0.2em] text-[var(--text-muted)]">
              Orchestra Microservices
            </Link>
            <h1 className="mt-1 font-heading text-4xl text-[var(--text-strong)]">Bảng điều khiển Frontend</h1>
            <p className="mt-2 text-sm text-[var(--text-base)]">
              Điều khiển playback, chỉnh tempo realtime, giám sát hệ thống và chạy Fault Demo theo BA handover baseline.
            </p>
          </div>
          <SessionBanner />
        </div>
        <nav className="mt-5 flex flex-wrap gap-2">
          {navItems.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`pill transition ${
                  active
                    ? "border-[var(--accent-strong)] bg-[var(--accent-soft)] text-[var(--accent-strong)]"
                    : "bg-[var(--card)] text-[var(--text-base)] hover:border-[var(--accent-strong)]"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </header>

      <section className="mt-6">{children}</section>
      <ToastViewport />
    </main>
  );
}
