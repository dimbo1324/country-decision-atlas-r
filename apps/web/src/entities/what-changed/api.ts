import { queryOptions } from "@tanstack/react-query";
import type { components } from "@country-decision-atlas/contracts/generated/types";
import { whatChangedApi } from "../../shared/api/what-changed";

type LocaleCode = components["schemas"]["LocaleCode"];

export function countryWhatChangedQuery(
  countrySlug: string,
  locale: LocaleCode,
) {
  return queryOptions({
    queryKey: ["country", countrySlug, "what-changed", locale] as const,
    queryFn: () => whatChangedApi.getCountryWhatChanged(countrySlug, { locale }),
    staleTime: 60_000,
  });
}
