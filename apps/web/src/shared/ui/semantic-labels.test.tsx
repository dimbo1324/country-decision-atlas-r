import { describe, expect, it } from "vitest";
import { confidenceLabel } from "./ConfidenceBadge";
import { trustLabel } from "./TrustBadge";

describe("confidenceLabel", () => {
  it("translates the three confidence levels per locale", () => {
    expect(confidenceLabel("high", "ru")).toBe("высокая");
    expect(confidenceLabel("medium", "ru")).toBe("средняя");
    expect(confidenceLabel("low", "ru")).toBe("низкая");
    expect(confidenceLabel("high", "en")).toBe("high");
    expect(confidenceLabel("high", "es")).toBe("alta");
  });

  it("falls back to the raw value for unknown levels", () => {
    expect(confidenceLabel("mystery", "en")).toBe("mystery");
  });
});

describe("trustLabel", () => {
  it("translates every trust level per locale", () => {
    expect(trustLabel("very_high", "ru")).toBe("Очень высокое");
    expect(trustLabel("high", "ru")).toBe("Высокое");
    expect(trustLabel("medium", "ru")).toBe("Среднее");
    expect(trustLabel("low", "ru")).toBe("Низкое");
    expect(trustLabel("very_low", "ru")).toBe("Очень низкое");
    expect(trustLabel("insufficient_data", "ru")).toBe("Недостаточно данных");
    expect(trustLabel("high", "en")).toBe("High");
    expect(trustLabel("high", "es")).toBe("Alta");
  });

  it("falls back to the raw value for unknown levels", () => {
    expect(trustLabel("unmapped", "en")).toBe("unmapped");
  });
});
