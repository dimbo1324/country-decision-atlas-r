import { queryOptions } from "@tanstack/react-query";
import type { components } from "@country-decision-atlas/contracts/generated/types";
import { whatChangedApi } from "../../shared/api/what-changed";

type LocaleCode = components["schemas"]["LocaleCode"];

const DISPLAY_LIMIT = 5;

export function countryWhatChangedQuery(
  countrySlug: string,
  locale: LocaleCode,
) {
  return queryOptions({
    queryKey: ["country", countrySlug, "what-changed", locale] as const,
    queryFn: () =>
      whatChangedApi.getCountryWhatChanged(countrySlug, {
        locale,
        days: 30,
        limit: DISPLAY_LIMIT,
      }),
    staleTime: 60_000,
  });
}
