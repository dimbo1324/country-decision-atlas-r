import { queryOptions } from "@tanstack/react-query";
import type { components } from "@country-decision-atlas/contracts/generated/types";
import { countryDriftApi } from "../../shared/api/country-drift";

type LocaleCode = components["schemas"]["LocaleCode"];

export function countryDriftQuery(countrySlug: string, locale: LocaleCode) {
  return queryOptions({
    queryKey: ["country", countrySlug, "drift", locale] as const,
    queryFn: () => countryDriftApi.getCountryDrift(countrySlug, locale),
    staleTime: 60_000,
  });
}
