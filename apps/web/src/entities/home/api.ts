import { queryOptions } from "@tanstack/react-query";
import { apiClient, unwrap } from "../../shared/api/client";
import type { SupportedLocale } from "../../shared/lib/locale";

export function homeOverviewQuery(locale: SupportedLocale) {
  return queryOptions({
    queryKey: ["home", "overview", locale] as const,
    queryFn: () =>
      unwrap(
        apiClient.GET("/api/v1/home/overview", {
          params: { query: { locale } },
        }),
      ),
    // Matches the platform summary's own refresh cadence — short enough
    // that "what changed" still feels live, long enough to not refetch on
    // every focus.
    staleTime: 60_000,
  });
}
