import { describe, expect, it } from "vitest";
import {
  capitalize,
  formatDate,
  formatDateTime,
  formatScore,
  formatWeight,
} from "./format";

describe("formatDate", () => {
  it("formats an ISO date string in Russian", () => {
    expect(formatDate("2026-01-15")).toBe("15 янв. 2026 г.");
  });

  it("returns an em dash for null or undefined", () => {
    expect(formatDate(null)).toBe("—");
    expect(formatDate(undefined)).toBe("—");
  });

  it("returns an em dash for an empty string", () => {
    expect(formatDate("")).toBe("—");
  });
});

describe("formatDateTime", () => {
  it("formats date and time in Russian", () => {
    expect(formatDateTime("2026-01-15T10:30:00Z")).toMatch(
      /15\.01\.2026, \d{2}:\d{2}:\d{2}/,
    );
  });

  it("returns an em dash for null or undefined", () => {
    expect(formatDateTime(null)).toBe("—");
    expect(formatDateTime(undefined)).toBe("—");
  });
});

describe("capitalize", () => {
  it("uppercases the first character", () => {
    expect(capitalize("высокая")).toBe("Высокая");
  });

  it("keeps an empty string empty", () => {
    expect(capitalize("")).toBe("");
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
