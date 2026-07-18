import type { components } from "@country-decision-atlas/contracts/generated/types";

import { DEFAULT_API_LOCALE } from "../lib/locale";
import { apiGet, queryString } from "./http";

type LocaleCode = components["schemas"]["LocaleCode"];
export type EligibilityFlag = components["schemas"]["EligibilityFlag"];
export type RouteType = components["schemas"]["RouteType"];
export type RouteListResponse = components["schemas"]["RouteListResponse"];
export type RouteListItem = components["schemas"]["RouteListItem"];
export type RouteDetailResponse = components["schemas"]["RouteDetailResponse"];
export type RouteEligibility = components["schemas"]["RouteEligibility"];

type ListCountryRoutesParams = {
  locale?: LocaleCode;
  route_type?: RouteType | "";
  allows_work?: EligibilityFlag | "";
  allows_family?: EligibilityFlag | "";
  leads_to_pr?: EligibilityFlag | "";
  limit?: number;
  offset?: number;
};

type RouteDetailParams = {
  locale?: LocaleCode;
};

export function listCountryRoutes(
  countrySlug: string,
  params: ListCountryRoutesParams = {},
): Promise<RouteListResponse> {
  return apiGet<RouteListResponse>(
    `/api/v1/countries/${countrySlug}/routes${queryString({
      locale: params.locale ?? DEFAULT_API_LOCALE,
      route_type: params.route_type,
      allows_work: params.allows_work,
      allows_family: params.allows_family,
      leads_to_pr: params.leads_to_pr,
      limit: params.limit,
      offset: params.offset,
    })}`,
  );
}

export function getRoute(
  routeId: string,
  params: RouteDetailParams = {},
): Promise<RouteDetailResponse> {
  return apiGet<RouteDetailResponse>(
    `/api/v1/routes/${routeId}${queryString({
      locale: params.locale ?? DEFAULT_API_LOCALE,
    })}`,
  );
}

export function getCountryRoute(
  countrySlug: string,
  routeSlug: string,
  params: RouteDetailParams = {},
): Promise<RouteDetailResponse> {
  return apiGet<RouteDetailResponse>(
    `/api/v1/countries/${countrySlug}/routes/${routeSlug}${queryString({
      locale: params.locale ?? DEFAULT_API_LOCALE,
    })}`,
  );
}

export const routesApi = {
  listCountryRoutes,
  getRoute,
  getCountryRoute,
};
