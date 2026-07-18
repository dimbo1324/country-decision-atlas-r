import type { components } from "@country-decision-atlas/contracts/generated/types";

export const SUPPORTED_LOCALES = ["en", "ru", "es"] as const;
export type SupportedLocale = (typeof SUPPORTED_LOCALES)[number];
export const DEFAULT_LOCALE: SupportedLocale = "en";

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

/** The backend's `LocaleCode` (data/content localization) only knows
 * `en`/`ru` — Spanish interface support is UI-chrome-only for now (the
 * owner's own scoping: translate the interface, not the data pipeline).
 * Every `shared/api/*` call that fetches locale-dependent country/content
 * data goes through this so an `es`-interface user still gets real
 * (English) data instead of a request the backend would reject. */
export type ApiLocale = components["schemas"]["LocaleCode"];

export function toApiLocale(locale: SupportedLocale): ApiLocale {
  return locale === "es" ? "en" : locale;
}

/** The `shared/api/*` hand-rolled modules' own internal fallback when no
 * locale is passed at all — kept distinct from `DEFAULT_LOCALE` (which is
 * the *interface's* default and now includes `es`) because these modules
 * are typed against `ApiLocale`/`LocaleCode`, not `SupportedLocale`. */
export const DEFAULT_API_LOCALE: ApiLocale = "en";
