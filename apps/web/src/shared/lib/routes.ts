export const routes = {
  home: "/",
  countries: "/countries",
  assistant: "/assistant",
  country: (slug: string) => `/countries/${slug}`,
  decision: "/decision",
  compare: "/compare",
  legalSignals: "/legal-signals",
  sources: "/sources",
  search: "/search",
  dataQuality: "/internal/data-quality",
  login: "/login",
  register: "/register",
  account: "/account",
  watchlist: "/watchlist",
  legalSignalsForCountry: (slug: string, locale: string) =>
    `/legal-signals?country_slug=${slug}&locale=${locale}`,
  sourcesForCountry: (slug: string, locale: string) =>
    `/sources?country_slug=${slug}&locale=${locale}`,
  countryWithLocale: (slug: string, locale: string) =>
    `/countries/${slug}?locale=${locale}`,
};

export function withLocale(href: string, locale: string) {
  const [pathname, query = ""] = href.split("?", 2);
  const params = new URLSearchParams(query);
  params.set("locale", locale);
  return `${pathname}?${params.toString()}`;
}
