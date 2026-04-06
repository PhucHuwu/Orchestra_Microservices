import { z } from "zod";

export const playbackFormSchema = z.object({
  score_id: z.string().uuid("Score ID phải là UUID hợp lệ"),
  initial_bpm: z.coerce.number().int().min(20).max(300)
});

export type PlaybackFormValues = z.infer<typeof playbackFormSchema>;
