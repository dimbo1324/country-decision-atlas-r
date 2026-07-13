import { queryOptions } from "@tanstack/react-query";
import type { components } from "@country-decision-atlas/contracts/generated/types";
import {
  listCountryRoutes,
  type EligibilityFlag,
  type RouteType,
} from "../../shared/api/routes";

type LocaleCode = components["schemas"]["LocaleCode"];

export interface CountryRoutesFilters {
  route_type: RouteType | "";
  allows_work: EligibilityFlag | "";
  allows_family: EligibilityFlag | "";
  leads_to_pr: EligibilityFlag | "";
}

export function countryRoutesQuery(
  countrySlug: string,
  locale: LocaleCode,
  filters: CountryRoutesFilters,
) {
  return queryOptions({
    queryKey: ["country", countrySlug, "routes", locale, filters] as const,
    queryFn: () =>
      listCountryRoutes(countrySlug, {
        locale,
        route_type: filters.route_type,
        allows_work: filters.allows_work,
        allows_family: filters.allows_family,
        leads_to_pr: filters.leads_to_pr,
        limit: 50,
        offset: 0,
      }),
    staleTime: 60_000,
    retry: false,
  });
}
