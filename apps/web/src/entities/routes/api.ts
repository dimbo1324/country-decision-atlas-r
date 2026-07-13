import { queryOptions } from "@tanstack/react-query";
import type { components } from "@country-decision-atlas/contracts/generated/types";
import { listCountryRoutes } from "../../shared/api/routes";

type LocaleCode = components["schemas"]["LocaleCode"];

export function countryRoutesQuery(countrySlug: string, locale: LocaleCode) {
  return queryOptions({
    queryKey: ["country", countrySlug, "routes", locale] as const,
    queryFn: () => listCountryRoutes(countrySlug, { locale }),
    staleTime: 60_000,
  });
}
