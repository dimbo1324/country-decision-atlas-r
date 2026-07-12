import { queryOptions } from "@tanstack/react-query";
import { apiClient, unwrap } from "../../shared/api/client";
import type { SupportedLocale } from "../../shared/lib/locale";

/**
 * Reference implementation of the plan's "one module per domain" data
 * pattern: a `queryOptions` factory usable both from a Server Component
 * (`queryClient.prefetchQuery(countryListQuery(...))` + `HydrationBoundary`)
 * and from a client component (`useQuery(countryListQuery(...))`). The
 * other 30 `shared/api/*` modules stay on the existing hand-rolled
 * `http.ts` wrapper for now — this is the pattern to migrate them to
 * incrementally, not a one-shot rewrite (Stage 3 scope is the
 * infrastructure, not the migration).
 */
export function countryListQuery(
  locale: SupportedLocale,
  params?: { limit?: number; offset?: number },
) {
  return queryOptions({
    queryKey: [
      "country",
      "list",
      locale,
      params?.limit,
      params?.offset,
    ] as const,
    queryFn: () =>
      unwrap(
        apiClient.GET("/api/v1/countries", {
          params: {
            query: {
              locale,
              limit: params?.limit,
              offset: params?.offset,
            },
          },
        }),
      ),
    // Country listings change on the order of days, not seconds.
    staleTime: 5 * 60_000,
  });
}
