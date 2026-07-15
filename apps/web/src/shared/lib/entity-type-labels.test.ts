import { describe, expect, it } from "vitest";
import type { SearchResultItem } from "../api/search";
import { ENTITY_TYPE_LABELS, entityTypeLabel } from "./entity-type-labels";

describe("entityTypeLabel", () => {
  it("translates every known entity type", () => {
    for (const [key, label] of Object.entries(ENTITY_TYPE_LABELS)) {
      expect(entityTypeLabel(key as SearchResultItem["entity_type"])).toBe(
        label,
      );
    }
  });

  it("falls back to the raw value for an unknown type", () => {
    expect(
      entityTypeLabel("unknown_kind" as SearchResultItem["entity_type"]),
    ).toBe("unknown_kind");
  });

  it("labels are non-empty Russian strings", () => {
    for (const label of Object.values(ENTITY_TYPE_LABELS)) {
      expect(label.length).toBeGreaterThan(0);
    }
  });
});
