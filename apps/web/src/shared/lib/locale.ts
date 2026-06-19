export const SUPPORTED_LOCALES = ["en", "ru"] as const;
export type SupportedLocale = (typeof SUPPORTED_LOCALES)[number];
export const DEFAULT_LOCALE: SupportedLocale = "en";

export function normalizeLocale(value: string | undefined | null): SupportedLocale {
  if (value === "ru") return "ru";
  return DEFAULT_LOCALE;
}

export function getLocaleFromSearchParams(
  searchParams: Record<string, string | string[] | undefined>,
): SupportedLocale {
  const raw = searchParams["locale"];
  return normalizeLocale(typeof raw === "string" ? raw : undefined);
}

export function resolveLocale(value?: string | null): SupportedLocale {
  return value === "ru" ? "ru" : "en";
}
