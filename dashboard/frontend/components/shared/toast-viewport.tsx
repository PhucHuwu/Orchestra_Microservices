"use client";

import { useToastStore } from "@/stores/toast-store";

function tone(type: "success" | "error" | "info") {
  if (type === "success") {
    return "border-[var(--accent-strong)] bg-[var(--accent-soft)] text-[var(--accent-strong)]";
  }
  if (type === "error") {
    return "border-[var(--danger)] bg-[var(--danger-soft)] text-[var(--danger)]";
  }
  return "border-[var(--border)] bg-[var(--card)] text-[var(--text-base)]";
}

export function ToastViewport() {
  const items = useToastStore((state) => state.items);

  return (
    <div className="pointer-events-none fixed bottom-4 right-4 z-50 flex w-[min(92vw,360px)] flex-col gap-2">
      {items.map((item) => (
        <div key={item.id} className={`fade-in pointer-events-auto rounded-xl border p-3 text-sm shadow-lg ${tone(item.type)}`}>
          <p className="font-semibold">{item.title}</p>
          {item.description ? <p className="mt-1 text-xs opacity-90">{item.description}</p> : null}
        </div>
      ))}
    </div>
  );
}
