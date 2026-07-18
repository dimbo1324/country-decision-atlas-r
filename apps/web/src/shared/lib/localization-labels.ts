import type { components } from "@country-decision-atlas/contracts/generated/types";
import type { SupportedLocale } from "./locale";

type LocalizationMeta = components["schemas"]["LocalizationMeta"];

export function formatLocaleCode(locale: string | null | undefined): string {
  if (!locale) return "";
  return locale.toUpperCase();
}

export function formatLocalePair(
  sourceLocale: string | null | undefined,
  resolvedLocale: string | null | undefined,
): string {
  const src = formatLocaleCode(sourceLocale);
  const res = formatLocaleCode(resolvedLocale);
  if (!src && !res) return "";
  if (!src) return res;
  if (!res) return src;
  if (src === res) return src;
  return `${src} → ${res}`;
}

const TRANSLATION_STATUS_LABELS: Record<
  SupportedLocale,
  Record<string, string>
> = {
  en: {
    original: "Original",
    human_authored: "Human-authored",
    machine_translated: "Machine translated",
    human_reviewed: "Reviewed by an editor",
    fallback: "Showing fallback",
    missing: "No translation",
    stale: "Stale translation",
    needs_review: "Needs review",
    source: "Source text",
    translated: "Translated",
  },
  ru: {
    original: "Оригинал",
    human_authored: "Написано вручную",
    machine_translated: "Машинный перевод",
    human_reviewed: "Проверено редактором",
    fallback: "Показан fallback",
    missing: "Нет перевода",
    stale: "Устаревший перевод",
    needs_review: "Требует проверки",
    source: "Исходный текст",
    translated: "Переведено",
  },
  es: {
    original: "Original",
    human_authored: "Redactado manualmente",
    machine_translated: "Traducción automática",
    human_reviewed: "Revisado por un editor",
    fallback: "Mostrando alternativa",
    missing: "Sin traducción",
    stale: "Traducción desactualizada",
    needs_review: "Necesita revisión",
    source: "Texto original",
    translated: "Traducido",
  },
};

export function getTranslationStatusLabel(
  status: string | null | undefined,
  locale: SupportedLocale,
): string {
  if (!status) return "";
  return TRANSLATION_STATUS_LABELS[locale][status] ?? "";
}

const BADGE_LABEL_TEXT: Record<
  SupportedLocale,
  {
    stale: string;
    missing: string;
    fallback: string;
    fallbackWithLocale: (resolved: string) => string;
    originalWithLocale: (resolved: string) => string;
  }
> = {
  en: {
    stale: "Stale translation",
    missing: "No translation",
    fallback: "Showing fallback",
    fallbackWithLocale: (resolved) => `Showing fallback ${resolved}`,
    originalWithLocale: (resolved) => `Original ${resolved}`,
  },
  ru: {
    stale: "Устаревший перевод",
    missing: "Нет перевода",
    fallback: "Показан fallback",
    fallbackWithLocale: (resolved) => `Показан fallback ${resolved}`,
    originalWithLocale: (resolved) => `Оригинал ${resolved}`,
  },
  es: {
    stale: "Traducción desactualizada",
    missing: "Sin traducción",
    fallback: "Mostrando alternativa",
    fallbackWithLocale: (resolved) => `Mostrando alternativa ${resolved}`,
    originalWithLocale: (resolved) => `Original ${resolved}`,
  },
};

export function getLocalizationBadgeLabel(
  meta: LocalizationMeta | null | undefined,
  locale: SupportedLocale,
): string | null {
  if (!meta) return null;
  const text = BADGE_LABEL_TEXT[locale];
  const resolved = formatLocaleCode(meta.resolved_locale);
  if (meta.has_stale_fields || meta.status === "stale") {
    return text.stale;
  }
  if (meta.status === "missing") {
    return text.missing;
  }
  if (meta.is_fallback) {
    return resolved ? text.fallbackWithLocale(resolved) : text.fallback;
  }
  if (meta.status === "machine_translated" || meta.has_machine_translation) {
    return getTranslationStatusLabel("machine_translated", locale);
  }
  if (meta.status === "human_reviewed" || meta.has_human_review) {
    return getTranslationStatusLabel("human_reviewed", locale);
  }
  if (meta.status === "original") {
    return resolved
      ? text.originalWithLocale(resolved)
      : getTranslationStatusLabel("original", locale);
  }
  if (meta.status === "human_authored") {
    return getTranslationStatusLabel("human_authored", locale);
  }
  if (meta.status === "needs_review") {
    return getTranslationStatusLabel("needs_review", locale);
  }
  return null;
}

const BADGE_TITLE_LABELS: Record<
  SupportedLocale,
  { requested: string; shown: string; status: string }
> = {
  en: {
    requested: "Requested language",
    shown: "Shown language",
    status: "Status",
  },
  ru: {
    requested: "Запрошенный язык",
    shown: "Показанный язык",
    status: "Статус",
  },
  es: {
    requested: "Idioma solicitado",
    shown: "Idioma mostrado",
    status: "Estado",
  },
};

export function getLocalizationBadgeTitle(
  meta: LocalizationMeta | null | undefined,
  locale: SupportedLocale,
): string | null {
  if (!meta) return null;
  const labels = BADGE_TITLE_LABELS[locale];
  const requested = formatLocaleCode(meta.requested_locale);
  const resolved = formatLocaleCode(meta.resolved_locale);
  const statusLabel =
    getTranslationStatusLabel(meta.status, locale) || meta.status;
  const parts: string[] = [];
  if (requested) parts.push(`${labels.requested}: ${requested}`);
  if (resolved) parts.push(`${labels.shown}: ${resolved}`);
  if (statusLabel) parts.push(`${labels.status}: ${statusLabel}`);
  return parts.length > 0 ? parts.join(". ") + "." : null;
}

export function getLocalizationBadgeVariant(
  meta: LocalizationMeta | null | undefined,
): string {
  if (!meta) return "";
  if (meta.has_stale_fields || meta.status === "stale") {
    return "localizationBadgeStale";
  }
  if (meta.status === "missing") {
    return "localizationBadgeMissing";
  }
  if (meta.is_fallback) {
    return "localizationBadgeFallback";
  }
  if (meta.status === "machine_translated" || meta.has_machine_translation) {
    return "localizationBadgeMachine";
  }
  if (meta.status === "human_reviewed" || meta.has_human_review) {
    return "localizationBadgeReviewed";
  }
  if (meta.status === "original" || meta.status === "human_authored") {
    return "localizationBadgeOriginal";
  }
  if (meta.status === "needs_review") {
    return "localizationBadgeNeedsReview";
  }
  return "";
}
