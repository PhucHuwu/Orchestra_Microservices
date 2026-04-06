import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { PlaybackControlForm } from "@/features/playback/playback-control-form";

describe("PlaybackControlForm", () => {
  it("calls start and stop handlers", () => {
    const onStart = vi.fn();
    const onStop = vi.fn();

    render(
      <PlaybackControlForm
        scoreId="11111111-1111-4111-8111-111111111111"
        bpm={120}
        validationMessage={null}
        startPending={false}
        stopPending={false}
        canStop={true}
        onScoreChange={() => {}}
        onBpmChange={() => {}}
        onStart={onStart}
        onStop={onStop}
      />
    );

    fireEvent.click(screen.getByRole("button", { name: "Start" }));
    fireEvent.click(screen.getByRole("button", { name: "Stop" }));

    expect(onStart).toHaveBeenCalledTimes(1);
    expect(onStop).toHaveBeenCalledTimes(1);
  });
});
