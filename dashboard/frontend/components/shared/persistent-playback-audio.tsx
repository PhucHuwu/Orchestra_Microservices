"use client";

import { useEffect, useMemo, useRef } from "react";

import { useSessionStore } from "@/stores/session-store";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export function PersistentPlaybackAudio() {
  const { status, audioToken } = useSessionStore();
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const wasPlayingRef = useRef<boolean>(false);
  const pendingSeekRef = useRef<number | null>(null);

  const src = useMemo(() => {
    if (!audioToken) {
      return "";
    }
    return `${API_BASE_URL}/api/v1/playback/audio/latest?t=${audioToken}`;
  }, [audioToken]);

  useEffect(() => {
    const element = audioRef.current;
    if (!element || !src) {
      return;
    }

    if (audioToken > 0) {
      wasPlayingRef.current = !element.paused && !element.ended;
      pendingSeekRef.current = Number.isFinite(element.currentTime) ? element.currentTime : 0;
    }

    const onCanPlay = () => {
      const target = pendingSeekRef.current;
      if (target !== null) {
        const clamped = Math.max(0, Math.min(target, Math.max(0, element.duration - 0.05)));
        pendingSeekRef.current = null;
        try {
          element.currentTime = clamped;
        } catch {
          // Ignore seek failures for streams that are not seekable yet.
        }
      }

      if (status === "running" && wasPlayingRef.current) {
        void element.play().catch(() => {
          // Browser autoplay policy can block play(). User can click Play manually.
        });
      }
    };

    const onLoadedMetadata = () => {
      const target = pendingSeekRef.current;
      if (target === null) {
        return;
      }
      const clamped = Math.max(0, Math.min(target, Math.max(0, element.duration - 0.05)));
      try {
        element.currentTime = clamped;
      } catch {
        // Ignore seek failures for streams that are not seekable yet.
      }
    };

    element.addEventListener("canplay", onCanPlay);
    element.addEventListener("loadedmetadata", onLoadedMetadata);
    element.load();
    if (status === "running" && !wasPlayingRef.current) {
      void element.play().catch(() => {
        // Browser autoplay policy can block play(). User can click Play manually.
      });
    }

    return () => {
      element.removeEventListener("canplay", onCanPlay);
      element.removeEventListener("loadedmetadata", onLoadedMetadata);
    };
  }, [src, status]);

  if (!src) {
    return null;
  }

  return (
    <div className="fixed bottom-3 left-1/2 z-50 w-[min(760px,92vw)] -translate-x-1/2 rounded-2xl border border-[var(--border)] bg-[color:var(--card)]/95 p-3 shadow-lg backdrop-blur">
      <p className="mb-2 text-xs text-[var(--text-muted)]">
        Audio player cố định ({status}) - tiếp tục phát khi chuyển trang
      </p>
      <audio ref={audioRef} controls className="w-full">
        <source src={src} type="audio/wav" />
      </audio>
    </div>
  );
}
