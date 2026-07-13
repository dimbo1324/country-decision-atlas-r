import {
  queryOptions,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";
import type { components } from "@country-decision-atlas/contracts/generated/types";
import { apiClient, unwrap } from "../../shared/api/client";
import { csrfHeaders } from "../../shared/auth/session";

type WatchlistResponse = components["schemas"]["WatchlistResponse"];
type WatchlistItem = components["schemas"]["WatchlistItem"];

const WATCHLIST_QUERY_KEY = ["me", "watchlist"] as const;

/** One fetch for an entire grid of cards — each `WatchlistStar` reads
 * membership from this shared cache instead of doing its own per-card
 * status request (see task-checklist.md design decisions, Stage 5). */
export function myWatchlistQuery() {
  return queryOptions({
    queryKey: WATCHLIST_QUERY_KEY,
    queryFn: () => unwrap(apiClient.GET("/api/v1/me/watchlist", {})),
    staleTime: 30_000,
  });
}

/** Optimistic add/remove: flips the star immediately, rolls back on error,
 * always re-syncs from the server afterwards. */
export function useToggleWatchlistMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      countrySlug,
      nextSaved,
    }: {
      countrySlug: string;
      countryName: string;
      nextSaved: boolean;
    }) => {
      if (nextSaved) {
        return unwrap(
          apiClient.POST("/api/v1/me/watchlist/countries/{country_slug}", {
            params: { path: { country_slug: countrySlug } },
            headers: csrfHeaders(),
          }),
        );
      }
      await unwrap(
        apiClient.DELETE("/api/v1/me/watchlist/countries/{country_slug}", {
          params: { path: { country_slug: countrySlug } },
          headers: csrfHeaders(),
        }),
      );
      return null;
    },
    onMutate: async ({ countrySlug, countryName, nextSaved }) => {
      await queryClient.cancelQueries({ queryKey: WATCHLIST_QUERY_KEY });
      const previous =
        queryClient.getQueryData<WatchlistResponse>(WATCHLIST_QUERY_KEY);
      queryClient.setQueryData<WatchlistResponse>(
        WATCHLIST_QUERY_KEY,
        (current) => {
          const items = current?.items ?? [];
          if (nextSaved) {
            if (items.some((item) => item.country_slug === countrySlug)) {
              return current;
            }
            const optimisticItem: WatchlistItem = {
              id: `optimistic-${countrySlug}`,
              country_slug: countrySlug,
              country_name: countryName,
              status: "active",
              notify_legal_signals: true,
              notify_drift_changes: true,
              notify_route_updates: true,
              notes: null,
              created_source: "web",
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            };
            return {
              total: (current?.total ?? 0) + 1,
              items: [...items, optimisticItem],
            };
          }
          const filtered = items.filter(
            (item) => item.country_slug !== countrySlug,
          );
          return { total: filtered.length, items: filtered };
        },
      );
      return { previous };
    },
    onError: (_error, _variables, context) => {
      if (context?.previous) {
        queryClient.setQueryData(WATCHLIST_QUERY_KEY, context.previous);
      }
    },
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: WATCHLIST_QUERY_KEY });
    },
  });
}
