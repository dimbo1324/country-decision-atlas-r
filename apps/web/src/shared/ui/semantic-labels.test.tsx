import { describe, expect, it } from "vitest";
import { confidenceLabelRu } from "./ConfidenceBadge";
import { trustLabelRu } from "./TrustBadge";

describe("confidenceLabelRu", () => {
  it("translates the three confidence levels", () => {
    expect(confidenceLabelRu("high")).toBe("высокая");
    expect(confidenceLabelRu("medium")).toBe("средняя");
    expect(confidenceLabelRu("low")).toBe("низкая");
  });

  it("falls back to the raw value for unknown levels", () => {
    expect(confidenceLabelRu("mystery")).toBe("mystery");
  });
});

describe("trustLabelRu", () => {
  it("translates every trust level", () => {
    expect(trustLabelRu("very_high")).toBe("Очень высокое");
    expect(trustLabelRu("high")).toBe("Высокое");
    expect(trustLabelRu("medium")).toBe("Среднее");
    expect(trustLabelRu("low")).toBe("Низкое");
    expect(trustLabelRu("very_low")).toBe("Очень низкое");
    expect(trustLabelRu("insufficient_data")).toBe("Недостаточно данных");
  });

  it("falls back to the raw value for unknown levels", () => {
    expect(trustLabelRu("unmapped")).toBe("unmapped");
  });
});
