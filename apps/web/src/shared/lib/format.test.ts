import { describe, expect, it } from "vitest";
import { formatDate, formatScore, formatWeight } from "./format";

describe("formatDate", () => {
  it("formats an ISO date string", () => {
    expect(formatDate("2026-01-15")).toBe("Jan 15, 2026");
  });

  it("returns an em dash for null or undefined", () => {
    expect(formatDate(null)).toBe("—");
    expect(formatDate(undefined)).toBe("—");
  });

  it("returns an em dash for an empty string", () => {
    expect(formatDate("")).toBe("—");
  });
});

describe("formatScore", () => {
  it("rounds and appends /100", () => {
    expect(formatScore(72.4)).toBe("72/100");
    expect(formatScore(72.6)).toBe("73/100");
  });
});

describe("formatWeight", () => {
  it("converts a 0..1 fraction to a rounded percentage", () => {
    expect(formatWeight(0.25)).toBe("25%");
    expect(formatWeight(0.333)).toBe("33%");
  });
});
