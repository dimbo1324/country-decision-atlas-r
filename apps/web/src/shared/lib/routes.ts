export const routes = {
  home: "/",
  countries: "/countries",
  country: (slug: string) => `/countries/${slug}`,
  decision: "/decision",
  compare: "/compare",
  legalSignals: "/legal-signals",
  sources: "/sources",
  dataQuality: "/internal/data-quality",
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
