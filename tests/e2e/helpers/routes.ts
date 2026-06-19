export const e2eRoutes = {
  home: "/",
  countries: "/countries",
  country: (slug: string, locale?: string) =>
    locale ? `/countries/${slug}?locale=${locale}` : `/countries/${slug}`,
  decision: (locale?: string) =>
    locale ? `/decision?locale=${locale}` : "/decision",
  legalSignals: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return `/legal-signals${qs}`;
  },
  sources: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return `/sources${qs}`;
  },
  dataQuality: "/internal/data-quality",
};
