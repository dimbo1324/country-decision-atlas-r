import { describe, expect, it } from "vitest";
import type { SearchResultItem } from "../api/search";
import { ENTITY_TYPE_LABELS, entityTypeLabel } from "./entity-type-labels";
import { SUPPORTED_LOCALES } from "./locale";

describe("entityTypeLabel", () => {
  for (const locale of SUPPORTED_LOCALES) {
    it(`translates every known entity type (${locale})`, () => {
      for (const [key, label] of Object.entries(ENTITY_TYPE_LABELS[locale])) {
        expect(
          entityTypeLabel(key as SearchResultItem["entity_type"], locale),
        ).toBe(label);
      }
    });

    it(`falls back to the raw value for an unknown type (${locale})`, () => {
      expect(
        entityTypeLabel(
          "unknown_kind" as SearchResultItem["entity_type"],
          locale,
        ),
      ).toBe("unknown_kind");
    });

    it(`labels are non-empty strings (${locale})`, () => {
      for (const label of Object.values(ENTITY_TYPE_LABELS[locale])) {
        expect(label.length).toBeGreaterThan(0);
      }
    });
  }
});
