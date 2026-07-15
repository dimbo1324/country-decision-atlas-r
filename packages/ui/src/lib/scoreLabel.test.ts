import { describe, expect, it } from "vitest";
import { scoreLabelStyle } from "./scoreLabel";

describe("scoreLabelStyle", () => {
  it("maps a known label to its accent and badge variant", () => {
    expect(scoreLabelStyle("excellent")).toEqual({
      accent: "sage",
      badgeVariant: "positive",
    });
  });

  it("falls back to 'missing' for an unrecognized label", () => {
    expect(scoreLabelStyle("unrecognized")).toEqual(scoreLabelStyle("missing"));
  });

  it("falls back to 'missing' for null or undefined", () => {
    expect(scoreLabelStyle(null)).toEqual(scoreLabelStyle("missing"));
    expect(scoreLabelStyle(undefined)).toEqual(scoreLabelStyle("missing"));
  });
});
