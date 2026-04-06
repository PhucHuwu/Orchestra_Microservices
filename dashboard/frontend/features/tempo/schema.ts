import { z } from "zod";

export const tempoFormSchema = z.object({
  new_bpm: z.coerce.number().int().min(20).max(300)
});

export type TempoFormValues = z.infer<typeof tempoFormSchema>;
