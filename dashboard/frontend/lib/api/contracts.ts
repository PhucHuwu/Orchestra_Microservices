import { z } from "zod";

export const successEnvelopeSchema = <T extends z.ZodTypeAny>(dataSchema: T) =>
  z.object({
    success: z.literal(true),
    data: dataSchema
  });

export const errorEnvelopeSchema = z.object({
  success: z.literal(false),
  error_code: z.string(),
  message: z.string()
});

export const playbackStatusSchema = z.enum(["running", "stopped", "failed"]);

export const playbackStartResponseSchema = z.object({
  session_id: z.string().uuid(),
  status: playbackStatusSchema
});

export const playbackStopResponseSchema = z.object({
  status: z.literal("stopped")
});

export const tempoResponseSchema = z.object({
  status: z.literal("accepted")
});

export const metricsOverviewSchema = z.object({
  queue_depth: z.record(z.string(), z.number().int().nonnegative()),
  consumer_count: z.record(z.string(), z.number().int().nonnegative()),
  message_rate: z.record(z.string(), z.number().nonnegative()),
  health_summary: z.object({
    healthy_services: z.number().int().nonnegative(),
    degraded_services: z.number().int().nonnegative()
  })
});

export const interactionEdgeSchema = z.object({
  from_service: z.string(),
  to_service: z.string(),
  queue: z.string(),
  depth: z.number().int().nonnegative(),
  consumers: z.number().int().nonnegative(),
  message_rate: z.number().nonnegative()
});

export const serviceToggleItemSchema = z.object({
  service_name: z.string(),
  enabled: z.boolean(),
  reachable: z.boolean(),
  worker_enabled: z.boolean().nullable().optional(),
  status: z.string(),
  message: z.string().nullable().optional()
});

export const serviceHealthItemSchema = z.object({
  service_name: z.string(),
  status: z.string(),
  latency_ms: z.number().int().nullable().optional(),
  queue_depth: z.number().int().nonnegative(),
  consumer_count: z.number().int().nonnegative(),
  captured_at: z.string().nullable().optional()
});

export const servicesHealthSchema = z.array(serviceHealthItemSchema);

export const metricsWsSchema = z.object({
  ts: z.string(),
  metrics: z.object({
    queue_depth: z.record(z.string(), z.number().int().nonnegative()),
    consumer_count: z.record(z.string(), z.number().int().nonnegative()),
    message_rate: z.record(z.string(), z.number().nonnegative()),
    health_summary: z.object({
      healthy_services: z.number().int().nonnegative(),
      degraded_services: z.number().int().nonnegative()
    }),
    services: servicesHealthSchema,
    interactions: interactionEdgeSchema.array(),
    toggles: serviceToggleItemSchema.array()
  })
});

export const scoreOptionSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  source_type: z.string(),
  source_path: z.string()
});

export const scoreUploadResponseSchema = scoreOptionSchema;

export type PlaybackStatus = z.infer<typeof playbackStatusSchema>;
export type PlaybackStartResponse = z.infer<typeof playbackStartResponseSchema>;
export type PlaybackStopResponse = z.infer<typeof playbackStopResponseSchema>;
export type TempoResponse = z.infer<typeof tempoResponseSchema>;
export type MetricsOverview = z.infer<typeof metricsOverviewSchema>;
export type ServiceHealthItem = z.infer<typeof serviceHealthItemSchema>;
export type MetricsWsPayload = z.infer<typeof metricsWsSchema>;
export type ScoreOption = z.infer<typeof scoreOptionSchema>;
export type InteractionEdge = z.infer<typeof interactionEdgeSchema>;
export type ServiceToggleItem = z.infer<typeof serviceToggleItemSchema>;
