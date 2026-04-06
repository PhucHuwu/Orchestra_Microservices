import { create } from "zustand";

import type { MetricsWsPayload } from "@/lib/api/contracts";

type SocketStatus = "connected" | "disconnected" | "reconnecting";

type MetricsState = {
  socketStatus: SocketStatus;
  latest: MetricsWsPayload | null;
  setSocketStatus: (status: SocketStatus) => void;
  setLatest: (payload: MetricsWsPayload) => void;
};

export const useMetricsStore = create<MetricsState>((set) => ({
  socketStatus: "disconnected",
  latest: null,
  setSocketStatus: (status) => set({ socketStatus: status }),
  setLatest: (payload) => set({ latest: payload })
}));
