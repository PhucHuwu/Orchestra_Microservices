import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { TempoControlForm } from "@/features/tempo/tempo-control-form";

describe("TempoControlForm", () => {
  it("calls apply handler", () => {
    const onApply = vi.fn();

    render(
      <TempoControlForm
        value={140}
        disabled={false}
        validationMessage={null}
        pending={false}
        onValueChange={() => {}}
        onApply={onApply}
      />
    );

    fireEvent.click(screen.getByRole("button", { name: "Apply BPM" }));
    expect(onApply).toHaveBeenCalledTimes(1);
  });
});
