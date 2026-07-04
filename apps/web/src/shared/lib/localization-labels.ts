import type { components } from "@country-decision-atlas/contracts/generated/types";

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

export function getTranslationStatusLabel(
  status: string | null | undefined,
): string {
  switch (status) {
    case "original":
      return "Оригинал";
    case "human_authored":
      return "Написано вручную";
    case "machine_translated":
      return "Машинный перевод";
    case "human_reviewed":
      return "Проверено редактором";
    case "fallback":
      return "Показан fallback";
    case "missing":
      return "Нет перевода";
    case "stale":
      return "Устаревший перевод";
    case "needs_review":
      return "Требует проверки";
    case "source":
      return "Исходный текст";
    case "translated":
      return "Переведено";
    default:
      return "";
  }
}

export function getLocalizationBadgeLabel(
  meta: LocalizationMeta | null | undefined,
): string | null {
  if (!meta) return null;
  const resolved = formatLocaleCode(meta.resolved_locale);
  if (meta.has_stale_fields || meta.status === "stale") {
    return "Устаревший перевод";
  }
  if (meta.status === "missing") {
    return "Нет перевода";
  }
  if (meta.is_fallback) {
    return resolved ? `Показан fallback ${resolved}` : "Показан fallback";
  }
  if (meta.status === "machine_translated" || meta.has_machine_translation) {
    return "Машинный перевод";
  }
  if (meta.status === "human_reviewed" || meta.has_human_review) {
    return "Проверено редактором";
  }
  if (meta.status === "original") {
    return resolved ? `Оригинал ${resolved}` : "Оригинал";
  }
  if (meta.status === "human_authored") {
    return "Написано вручную";
  }
  if (meta.status === "needs_review") {
    return "Требует проверки";
  }
  return null;
}

export function getLocalizationBadgeTitle(
  meta: LocalizationMeta | null | undefined,
): string | null {
  if (!meta) return null;
  const requested = formatLocaleCode(meta.requested_locale);
  const resolved = formatLocaleCode(meta.resolved_locale);
  const statusLabel = getTranslationStatusLabel(meta.status) || meta.status;
  const parts: string[] = [];
  if (requested) parts.push(`Запрошенный язык: ${requested}`);
  if (resolved) parts.push(`Показанный язык: ${resolved}`);
  if (statusLabel) parts.push(`Статус: ${statusLabel}`);
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
