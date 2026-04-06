import {
  metricsOverviewSchema,
  playbackStartResponseSchema,
  playbackStopResponseSchema,
  servicesHealthSchema,
  tempoResponseSchema
} from "@/lib/api/contracts";
import { apiGet, apiPost } from "@/lib/api/client";

export type StartPlaybackBody = {
  score_id: string;
  initial_bpm: number;
};

export type StopPlaybackBody = {
  session_id: string;
};

export type TempoBody = {
  session_id: string;
  new_bpm: number;
};

export async function startPlayback(body: StartPlaybackBody) {
  return apiPost("/api/v1/playback/start", body, playbackStartResponseSchema);
}

export async function stopPlayback(body: StopPlaybackBody) {
  return apiPost("/api/v1/playback/stop", body, playbackStopResponseSchema);
}

export async function applyTempo(body: TempoBody) {
  return apiPost("/api/v1/tempo", body, tempoResponseSchema);
}

export async function fetchMetricsOverview() {
  return apiGet("/api/v1/metrics/overview", metricsOverviewSchema);
}

export async function fetchServicesHealth() {
  return apiGet("/api/v1/services/health", servicesHealthSchema);
}
