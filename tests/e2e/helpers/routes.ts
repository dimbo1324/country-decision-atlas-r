export const e2eRoutes = {
  home: "/",
  assistant: (locale?: string) =>
    locale ? `/assistant?locale=${locale}` : "/assistant",
  countries: "/countries",
  country: (slug: string, locale?: string) =>
    locale ? `/countries/${slug}?locale=${locale}` : `/countries/${slug}`,
  routeDetail: (id: string, locale?: string) =>
    locale ? `/routes/${id}?locale=${locale}` : `/routes/${id}`,
  decision: (locale?: string) =>
    locale ? `/decision?locale=${locale}` : "/decision",
  compare: "/compare",
  legalSignals: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return `/legal-signals${qs}`;
  },
  sources: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return `/sources${qs}`;
  },
  search: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return `/search${qs}`;
  },
  dataQuality: "/internal/data-quality",
  migrationBoard: "/migration-board",
  migrationBoardNew: "/migration-board/new",
  accountMigrationBoard: "/account/migration-board",
  migrationBoardModeration: "/internal/migration-board-moderation",
  login: "/login",
  register: "/register",
  account: "/account",
  watchlist: "/watchlist",
};
