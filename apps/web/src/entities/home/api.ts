import { queryOptions } from "@tanstack/react-query";
import { apiClient, unwrap } from "../../shared/api/client";
import { toApiLocale, type SupportedLocale } from "../../shared/lib/locale";

export function homeOverviewQuery(locale: SupportedLocale) {
  const apiLocale = toApiLocale(locale);
  return queryOptions({
    queryKey: ["home", "overview", apiLocale] as const,
    queryFn: () =>
      unwrap(
        apiClient.GET("/api/v1/home/overview", {
          params: { query: { locale: apiLocale } },
        }),
      ),
    // Matches the platform summary's own refresh cadence — short enough
    // that "what changed" still feels live, long enough to not refetch on
    // every focus.
    staleTime: 60_000,
  });
}
