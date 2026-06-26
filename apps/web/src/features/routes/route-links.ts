import type { LocaleCode } from "../../shared/api/countries";

export function routeDetailPath(routeId: string, locale: LocaleCode) {
  return `/routes/${routeId}?locale=${locale}`;
}
