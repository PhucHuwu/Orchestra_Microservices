import { describe, expect, it } from "vitest";

import { playbackFormSchema } from "@/features/playback/schema";

describe("playbackFormSchema", () => {
  it("accepts valid payload", () => {
    const parsed = playbackFormSchema.safeParse({
      score_id: "11111111-1111-4111-8111-111111111111",
      initial_bpm: 120
    });
    expect(parsed.success).toBe(true);
  });

  it("rejects bpm out of range", () => {
    const parsed = playbackFormSchema.safeParse({
      score_id: "11111111-1111-4111-8111-111111111111",
      initial_bpm: 10
    });
    expect(parsed.success).toBe(false);
  });
});
