import { create } from "zustand";

import type { PlaybackStatus } from "@/lib/api/contracts";

type SessionState = {
  sessionId: string | null;
  status: PlaybackStatus;
  currentBpm: number | null;
  tempoUpdatedAt: string | null;
  audioToken: number;
  setRunning: (payload: { sessionId: string; bpm: number }) => void;
  setStopped: () => void;
  setFailed: () => void;
  setTempo: (payload: { bpm: number; updatedAt: string }) => void;
  bumpAudioToken: () => void;
};

export const useSessionStore = create<SessionState>((set) => ({
  sessionId: null,
  status: "stopped",
  currentBpm: null,
  tempoUpdatedAt: null,
  audioToken: 0,
  setRunning: ({ sessionId, bpm }) =>
    set({
      sessionId,
      status: "running",
      currentBpm: bpm,
      tempoUpdatedAt: new Date().toISOString(),
      audioToken: Date.now()
    }),
  setStopped: () => set({ status: "stopped", sessionId: null }),
  setFailed: () => set({ status: "failed" }),
  setTempo: ({ bpm, updatedAt }) => set({ currentBpm: bpm, tempoUpdatedAt: updatedAt }),
  bumpAudioToken: () => set({ audioToken: Date.now() })
}));
