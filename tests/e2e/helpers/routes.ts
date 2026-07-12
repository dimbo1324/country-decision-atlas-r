const DEFAULT_LOCALE = "ru";

/** Path-based locale (always-prefixed, e.g. `/ru/countries`) replaced the
 * old `?locale=` query param in Stage 3. Every route here still defaults to
 * `ru` when no locale is given, matching the old default-locale behavior,
 * so call sites that never cared about locale don't need to change. */
function withLocale(path: string, locale?: string): string {
  return `/${locale ?? DEFAULT_LOCALE}${path}`;
}

/** `legalSignals`/`sources`/`search` historically took `locale` as just
 * another key in the params object (serialized into the query string).
 * Pulling it out here — instead of changing every call site to pass it
 * separately — means the ~30 existing `{ ..., locale: "ru" }` call sites
 * across the suite keep working unchanged; the value now becomes the path
 * prefix instead of a query param. */
function pathWithQuery(base: string, params?: Record<string, string>): string {
  const { locale, ...rest } = params ?? {};
  const qs = Object.keys(rest).length
    ? "?" + new URLSearchParams(rest).toString()
    : "";
  return withLocale(`${base}${qs}`, locale);
}

export const e2eRoutes = {
  home: withLocale(""),
  assistant: (locale?: string) => withLocale("/assistant", locale),
  countries: withLocale("/countries"),
  country: (slug: string, locale?: string) =>
    withLocale(`/countries/${slug}`, locale),
  routeDetail: (id: string, locale?: string) =>
    withLocale(`/routes/${id}`, locale),
  decision: (locale?: string) => withLocale("/decision", locale),
  compare: withLocale("/compare"),
  legalSignals: (params?: Record<string, string>) =>
    pathWithQuery("/legal-signals", params),
  sources: (params?: Record<string, string>) =>
    pathWithQuery("/sources", params),
  search: (params?: Record<string, string>) => pathWithQuery("/search", params),
  dataQuality: "/internal/data-quality",
  migrationBoard: withLocale("/migration-board"),
  migrationBoardNew: withLocale("/migration-board/new"),
  accountMigrationBoard: withLocale("/account/migration-board"),
  migrationBoardModeration: "/internal/migration-board-moderation",
  login: withLocale("/login"),
  register: withLocale("/register"),
  account: withLocale("/account"),
  watchlist: withLocale("/watchlist"),
};
