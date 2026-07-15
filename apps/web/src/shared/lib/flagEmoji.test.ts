import { describe, expect, it } from "vitest";
import { flagEmoji } from "./flagEmoji";

describe("flagEmoji", () => {
  it("builds a flag from a lowercase ISO 3166-1 alpha-2 code", () => {
    expect(flagEmoji("ru")).toBe("🇷🇺");
  });

  it("builds a flag from an uppercase code", () => {
    expect(flagEmoji("US")).toBe("🇺🇸");
  });

  it("trims surrounding whitespace before validating", () => {
    expect(flagEmoji("  de ")).toBe("🇩🇪");
  });

  it("returns an empty string for codes that are not exactly two letters", () => {
    expect(flagEmoji("rus")).toBe("");
    expect(flagEmoji("r")).toBe("");
    expect(flagEmoji("")).toBe("");
  });

  it("returns an empty string for non-letter input", () => {
    expect(flagEmoji("12")).toBe("");
  });
});
