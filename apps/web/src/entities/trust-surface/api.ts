import { queryOptions } from "@tanstack/react-query";
import type { components } from "@country-decision-atlas/contracts/generated/types";
import { trustApi } from "../../shared/api/trust";

type LocaleCode = components["schemas"]["LocaleCode"];

export function countryTrustQuery(countrySlug: string, locale: LocaleCode) {
  return queryOptions({
    queryKey: ["country", countrySlug, "trust", locale] as const,
    queryFn: () => trustApi.getCountryTrust(countrySlug, locale),
    staleTime: 60_000,
    retry: false,
  });
}
