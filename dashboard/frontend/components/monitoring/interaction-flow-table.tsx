"use client";

import type { InteractionEdge } from "@/lib/api/contracts";

type Props = {
  edges: InteractionEdge[];
};

export function InteractionFlowTable({ edges }: Props) {
  if (edges.length === 0) {
    return <p className="text-sm text-[var(--text-muted)]">Chưa có interaction edge nào.</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="text-left text-[var(--text-muted)]">
            <th className="py-2">Từ service</th>
            <th className="py-2">Đến service</th>
            <th className="py-2">Queue</th>
            <th className="py-2">Depth</th>
            <th className="py-2">Consumers</th>
            <th className="py-2">Rate</th>
          </tr>
        </thead>
        <tbody>
          {edges.map((edge) => (
            <tr key={`${edge.from_service}-${edge.to_service}-${edge.queue}`} className="border-t border-[var(--border)]">
              <td className="py-2">{edge.from_service}</td>
              <td className="py-2">{edge.to_service}</td>
              <td className="py-2">{edge.queue}</td>
              <td className="py-2">{edge.depth}</td>
              <td className="py-2">{edge.consumers}</td>
              <td className="py-2">{edge.message_rate.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
