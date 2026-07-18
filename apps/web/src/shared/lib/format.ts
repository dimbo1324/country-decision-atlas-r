import type { SupportedLocale } from "./locale";

export const DATE_FORMAT_LOCALE: Record<SupportedLocale, string> = {
  en: "en-US",
  ru: "ru-RU",
  es: "es-ES",
};

/** `locale` defaults to `"ru"` (not the interface's own `DEFAULT_LOCALE`)
 * so the handful of remaining callers that haven't been migrated to pass
 * a real locale yet -- currently only `/internal/**` admin pages, out of
 * this task's scope -- keep their exact current Russian-formatted output
 * with no required edit on their part. */
export function formatDate(
  value: string | null | undefined,
  locale: SupportedLocale = "ru",
): string {
  if (!value) return "—";
  return new Date(value).toLocaleDateString(DATE_FORMAT_LOCALE[locale], {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function formatDateTime(
  value: string | null | undefined,
  locale: SupportedLocale = "ru",
): string {
  if (!value) return "—";
  return new Date(value).toLocaleString(DATE_FORMAT_LOCALE[locale]);
}

export function formatScore(value: number): string {
  return `${Math.round(value)}/100`;
}

export function formatWeight(value: number): string {
  return `${(value * 100).toFixed(0)}%`;
}

export function capitalize(value: string): string {
  return value.length === 0 ? value : value[0].toUpperCase() + value.slice(1);
}
