import {
  metricsOverviewSchema,
  playbackStartResponseSchema,
  playbackStopResponseSchema,
  scoreOptionSchema,
  scoreUploadResponseSchema,
  serviceToggleItemSchema,
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
  return apiPost("/api/v1/playback/start", body, playbackStartResponseSchema, { timeoutMs: 60000 });
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

export async function fetchScores() {
  return apiGet("/api/v1/scores", scoreOptionSchema.array());
}

export async function uploadScore(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  return apiPost("/api/v1/scores/upload", formData, scoreUploadResponseSchema);
}

export async function fetchServiceControls() {
  return apiGet("/api/v1/services/control", serviceToggleItemSchema.array());
}

export async function setServiceControl(body: { service_name: string; enabled: boolean }) {
  return apiPost("/api/v1/services/control", body, serviceToggleItemSchema);
}
