export const SUPPORTED_LOCALES = ["en", "ru"] as const;
export type SupportedLocale = (typeof SUPPORTED_LOCALES)[number];
export const DEFAULT_LOCALE: SupportedLocale = "ru";

/** next-intl's `useLocale()`/`getLocale()` return a plain `string` (the
 * installed version doesn't support typed-locale augmentation) — this
 * narrows it to `SupportedLocale` for the many `shared/api/*` calls typed
 * against the contract's locale enum. The value is always one of
 * routing.locales in practice; the fallback only matters for the type. */
export function asSupportedLocale(locale: string): SupportedLocale {
  return (SUPPORTED_LOCALES as readonly string[]).includes(locale)
    ? (locale as SupportedLocale)
    : DEFAULT_LOCALE;
}
