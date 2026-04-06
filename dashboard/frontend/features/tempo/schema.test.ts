import { describe, expect, it } from "vitest";

import { tempoFormSchema } from "@/features/tempo/schema";

describe("tempoFormSchema", () => {
  it("accepts valid bpm", () => {
    expect(tempoFormSchema.safeParse({ new_bpm: 140 }).success).toBe(true);
  });

  it("rejects invalid bpm", () => {
    expect(tempoFormSchema.safeParse({ new_bpm: 301 }).success).toBe(false);
  });
});
