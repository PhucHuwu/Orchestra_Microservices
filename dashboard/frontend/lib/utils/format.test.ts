import { describe, expect, it } from "vitest";

import { formatDateTime, toTitle } from "@/lib/utils/format";

describe("format utils", () => {
  it("formats valid datetime", () => {
    const result = formatDateTime("2026-04-06T10:10:00Z");
    expect(result).not.toBe("-");
  });

  it("returns dash for invalid datetime", () => {
    expect(formatDateTime("not-a-date")).toBe("-");
    expect(formatDateTime(null)).toBe("-");
  });

  it("converts dotted names to title", () => {
    expect(toTitle("playback.output")).toBe("Playback Output");
  });
});
