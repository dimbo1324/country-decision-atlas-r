import { queryOptions } from "@tanstack/react-query";
import { apiClient, unwrap } from "../../shared/api/client";
import { toApiLocale, type SupportedLocale } from "../../shared/lib/locale";

export interface SearchQueryParams {
  q: string;
  locale: SupportedLocale;
  types?: string;
  countrySlug?: string;
  limit?: number;
  offset?: number;
}

/** Caller decides `enabled` (e.g. `q.trim().length > 0`) — this factory
 * stays a plain queryOptions object so it works the same for a debounced
 * ⌘K palette query and the full `/search` page. */
export function searchQuery(params: SearchQueryParams) {
  const apiLocale = toApiLocale(params.locale);
  return queryOptions({
    queryKey: [
      "search",
      params.q,
      apiLocale,
      params.types,
      params.countrySlug,
      params.limit,
      params.offset,
    ] as const,
    queryFn: () =>
      unwrap(
        apiClient.GET("/api/v1/search", {
          params: {
            query: {
              q: params.q,
              locale: apiLocale,
              types: params.types,
              country_slug: params.countrySlug,
              limit: params.limit,
              offset: params.offset,
            },
          },
        }),
      ),
    staleTime: 30_000,
  });
}
