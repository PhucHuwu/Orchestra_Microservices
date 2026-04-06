import MockAdapter from "axios-mock-adapter";
import { describe, expect, it, beforeEach, afterAll } from "vitest";
import { z } from "zod";

import { apiGet, apiPost, ApiClientError, http } from "@/lib/api/client";

const mock = new MockAdapter(http);

describe("api client", () => {
  beforeEach(() => {
    mock.reset();
  });

  afterAll(() => {
    mock.restore();
  });

  it("parses success envelope for GET", async () => {
    mock.onGet("http://localhost:8000/api/v1/metrics/overview").reply(200, {
      success: true,
      data: { value: 1 }
    });

    const data = await apiGet("/api/v1/metrics/overview", z.object({ value: z.number() }));
    expect(data.value).toBe(1);
  });

  it("maps backend error envelope", async () => {
    mock.onPost("http://localhost:8000/api/v1/tempo").reply(400, {
      success: false,
      error_code: "INVALID_SESSION",
      message: "Session not found"
    });

    await expect(
      apiPost("/api/v1/tempo", { session_id: "x", new_bpm: 120 }, z.object({ status: z.string() }))
    ).rejects.toBeInstanceOf(ApiClientError);
  });
});
