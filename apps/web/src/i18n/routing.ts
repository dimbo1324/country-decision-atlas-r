import { defineRouting } from "next-intl/routing";
import { DEFAULT_LOCALE, SUPPORTED_LOCALES } from "../shared/lib/locale";

export const routing = defineRouting({
  locales: SUPPORTED_LOCALES,
  defaultLocale: DEFAULT_LOCALE,
  localePrefix: "always",
  // The product has always defaulted to ru regardless of browser language
  // (no query param meant ru, full stop) — auto-detecting from
  // Accept-Language would silently change that default for e.g. any
  // English-locale browser/CI environment.
  localeDetection: false,
});
