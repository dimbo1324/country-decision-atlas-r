import { queryOptions } from "@tanstack/react-query";
import type { components } from "@country-decision-atlas/contracts/generated/types";
import { countryDriftApi } from "../../shared/api/country-drift";

type LocaleCode = components["schemas"]["LocaleCode"];

export function countryDriftQuery(countrySlug: string, locale: LocaleCode) {
  return queryOptions({
    queryKey: ["country", countrySlug, "drift", locale] as const,
    queryFn: () => countryDriftApi.getCountryDrift(countrySlug, locale),
    staleTime: 60_000,
    // A per-country side-fetch on the dossier: fail fast on error, same as
    // the plain-fetch code this replaced. The global default (retry: 1)
    // would double a client-side timeout's latency before the error state
    // shows, breaking tests that assert it within a fixed window.
    retry: false,
  });
}
