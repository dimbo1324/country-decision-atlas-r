import { describe, expect, it } from "vitest";
import { withAlpha } from "./color";

describe("withAlpha", () => {
  it("converts a hex color to an rgba string", () => {
    expect(withAlpha("#ff0000", 0.5)).toBe("rgba(255, 0, 0, 0.5)");
  });

  it("accepts a hex color without the leading #", () => {
    expect(withAlpha("00ff00", 1)).toBe("rgba(0, 255, 0, 1)");
  });
});
