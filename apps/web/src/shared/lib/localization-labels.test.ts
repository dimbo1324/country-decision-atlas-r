import { describe, expect, it } from "vitest";
import {
  formatLocaleCode,
  formatLocalePair,
  getLocalizationBadgeLabel,
  getLocalizationBadgeTitle,
  getLocalizationBadgeVariant,
  getTranslationStatusLabel,
} from "./localization-labels";
import type { components } from "@country-decision-atlas/contracts/generated/types";

type LocalizationMeta = components["schemas"]["LocalizationMeta"];

function meta(overrides: Partial<LocalizationMeta>): LocalizationMeta {
  return {
    requested_locale: null,
    resolved_locale: null,
    status: null,
    is_fallback: false,
    has_stale_fields: false,
    has_machine_translation: false,
    has_human_review: false,
    ...overrides,
  } as LocalizationMeta;
}

describe("formatLocaleCode", () => {
  it("uppercases a locale code", () => {
    expect(formatLocaleCode("ru")).toBe("RU");
  });

  it("returns an empty string for null/undefined", () => {
    expect(formatLocaleCode(null)).toBe("");
    expect(formatLocaleCode(undefined)).toBe("");
  });
});

describe("formatLocalePair", () => {
  it("joins two different locales with an arrow", () => {
    expect(formatLocalePair("en", "ru")).toBe("EN → RU");
  });

  it("collapses to one code when both locales match", () => {
    expect(formatLocalePair("ru", "ru")).toBe("RU");
  });

  it("falls back to whichever single locale is present", () => {
    expect(formatLocalePair(null, "ru")).toBe("RU");
    expect(formatLocalePair("ru", null)).toBe("RU");
  });

  it("returns an empty string when both are missing", () => {
    expect(formatLocalePair(null, null)).toBe("");
  });
});

describe("getTranslationStatusLabel", () => {
  it("maps every known status to a locale-specific label", () => {
    expect(getTranslationStatusLabel("original", "ru")).toBe("Оригинал");
    expect(getTranslationStatusLabel("machine_translated", "ru")).toBe(
      "Машинный перевод",
    );
    expect(getTranslationStatusLabel("stale", "ru")).toBe("Устаревший перевод");
    expect(getTranslationStatusLabel("original", "en")).toBe("Original");
    expect(getTranslationStatusLabel("original", "es")).toBe("Original");
  });

  it("returns an empty string for an unknown or missing status", () => {
    expect(getTranslationStatusLabel("unknown", "en")).toBe("");
    expect(getTranslationStatusLabel(null, "en")).toBe("");
  });
});

describe("getLocalizationBadgeLabel", () => {
  it("returns null when meta is missing", () => {
    expect(getLocalizationBadgeLabel(null, "en")).toBeNull();
  });

  it("prioritizes stale over other statuses", () => {
    expect(
      getLocalizationBadgeLabel(
        meta({ has_stale_fields: true, status: "original" }),
        "ru",
      ),
    ).toBe("Устаревший перевод");
  });

  it("reports missing translation", () => {
    expect(getLocalizationBadgeLabel(meta({ status: "missing" }), "ru")).toBe(
      "Нет перевода",
    );
  });

  it("includes the resolved locale for a fallback", () => {
    expect(
      getLocalizationBadgeLabel(
        meta({ is_fallback: true, resolved_locale: "en" }),
        "ru",
      ),
    ).toBe("Показан fallback EN");
  });

  it("includes the resolved locale for an original", () => {
    expect(
      getLocalizationBadgeLabel(
        meta({ status: "original", resolved_locale: "ru" }),
        "ru",
      ),
    ).toBe("Оригинал RU");
  });

  it("returns null for an unrecognized status", () => {
    expect(
      getLocalizationBadgeLabel(meta({ status: "weird" }), "ru"),
    ).toBeNull();
  });

  it("translates the same meta into English and Spanish", () => {
    expect(getLocalizationBadgeLabel(meta({ status: "missing" }), "en")).toBe(
      "No translation",
    );
    expect(getLocalizationBadgeLabel(meta({ status: "missing" }), "es")).toBe(
      "Sin traducción",
    );
  });
});

describe("getLocalizationBadgeTitle", () => {
  it("returns null when meta is missing", () => {
    expect(getLocalizationBadgeTitle(null, "ru")).toBeNull();
  });

  it("joins requested/resolved/status into one sentence", () => {
    expect(
      getLocalizationBadgeTitle(
        meta({
          requested_locale: "en",
          resolved_locale: "ru",
          status: "fallback",
        }),
        "ru",
      ),
    ).toBe(
      "Запрошенный язык: EN. Показанный язык: RU. Статус: Показан fallback.",
    );
  });

  it("returns null when there is nothing to report", () => {
    expect(getLocalizationBadgeTitle(meta({}), "ru")).toBeNull();
  });
});

describe("getLocalizationBadgeVariant", () => {
  it("returns an empty string when meta is missing", () => {
    expect(getLocalizationBadgeVariant(null)).toBe("");
  });

  it("maps stale before other flags", () => {
    expect(getLocalizationBadgeVariant(meta({ has_stale_fields: true }))).toBe(
      "localizationBadgeStale",
    );
  });

  it("maps machine translation", () => {
    expect(
      getLocalizationBadgeVariant(meta({ has_machine_translation: true })),
    ).toBe("localizationBadgeMachine");
  });

  it("returns an empty string for an unrecognized status", () => {
    expect(getLocalizationBadgeVariant(meta({ status: "weird" }))).toBe("");
  });
});
