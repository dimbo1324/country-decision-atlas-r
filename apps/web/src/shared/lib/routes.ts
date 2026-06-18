export const routes = {
  home: "/",
  countries: "/countries",
  country: (slug: string) => `/countries/${slug}`,
  decision: "/decision",
  legalSignals: "/legal-signals",
  sources: "/sources",
  dataQuality: "/internal/data-quality",
};
