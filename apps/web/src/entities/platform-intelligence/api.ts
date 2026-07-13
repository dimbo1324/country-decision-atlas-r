import { queryOptions } from "@tanstack/react-query";
import type { components } from "@country-decision-atlas/contracts/generated/types";
import { platformMetricsApi } from "../../shared/api/platform-metrics";

type LocaleCode = components["schemas"]["LocaleCode"];

export function countryPlatformMetricsQuery(
  countrySlug: string,
  locale: LocaleCode,
) {
  return queryOptions({
    queryKey: ["country", countrySlug, "platform-metrics", locale] as const,
    queryFn: () =>
      platformMetricsApi.getCountryPlatformMetrics(countrySlug, locale),
    staleTime: 60_000,
    retry: false,
  });
}
