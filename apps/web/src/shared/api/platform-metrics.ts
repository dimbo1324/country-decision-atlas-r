import type { components } from "@country-decision-atlas/contracts/generated/types";

import { DEFAULT_API_LOCALE } from "../lib/locale";
import { apiGet, queryString } from "./http";

type LocaleCode = components["schemas"]["LocaleCode"];
export type PlatformMetric = components["schemas"]["PlatformMetric"];
export type PlatformMetricListResponse =
  components["schemas"]["PlatformMetricListResponse"];
export type PlatformMetricDetailResponse =
  components["schemas"]["PlatformMetricDetailResponse"];

export function getCountryPlatformMetrics(
  countrySlug: string,
  locale: LocaleCode = DEFAULT_API_LOCALE,
  scenario?: string,
  includeInputSummary = false,
): Promise<PlatformMetricListResponse> {
  return apiGet<PlatformMetricListResponse>(
    `/api/v1/countries/${countrySlug}/platform-metrics${queryString({
      locale,
      ...(scenario ? { scenario } : {}),
      include_input_summary: includeInputSummary,
    })}`,
  );
}

export function getCountryPlatformMetric(
  countrySlug: string,
  metricKey: string,
  locale: LocaleCode = DEFAULT_API_LOCALE,
  scenario?: string,
): Promise<PlatformMetricDetailResponse> {
  return apiGet<PlatformMetricDetailResponse>(
    `/api/v1/countries/${countrySlug}/platform-metrics/${metricKey}${queryString(
      {
        locale,
        ...(scenario ? { scenario } : {}),
      },
    )}`,
  );
}

export const platformMetricsApi = {
  getCountryPlatformMetrics,
  getCountryPlatformMetric,
};
