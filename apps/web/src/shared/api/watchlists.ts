import type { components } from "@country-decision-atlas/contracts/generated/types";
import { csrfHeaders } from "../auth/session";
import { apiDelete, apiGet, apiPatch, apiPost } from "./http";

export type WatchlistItem = components["schemas"]["WatchlistItem"];
export type WatchlistResponse = components["schemas"]["WatchlistResponse"];
export type WatchlistStatusResponse =
  components["schemas"]["WatchlistStatusResponse"];

type WatchlistPreferencesUpdate = {
  notify_legal_signals?: boolean;
  notify_drift_changes?: boolean;
  notify_route_updates?: boolean;
  notes?: string | null;
};

export function listWatchlist(): Promise<WatchlistResponse> {
  return apiGet<WatchlistResponse>("/api/v1/me/watchlist", {
    headers: csrfHeaders(),
  });
}

export function addCountryToWatchlist(
  countrySlug: string,
): Promise<WatchlistItem> {
  return apiPost<WatchlistItem, Record<string, never>>(
    `/api/v1/me/watchlist/countries/${countrySlug}`,
    {},
    { headers: csrfHeaders() },
  );
}

export function removeCountryFromWatchlist(countrySlug: string): Promise<void> {
  return apiDelete<void>(`/api/v1/me/watchlist/countries/${countrySlug}`, {
    headers: csrfHeaders(),
  });
}

export function updateWatchlistPreferences(
  countrySlug: string,
  payload: WatchlistPreferencesUpdate,
): Promise<WatchlistItem> {
  return apiPatch<WatchlistItem, WatchlistPreferencesUpdate>(
    `/api/v1/me/watchlist/countries/${countrySlug}`,
    payload,
    { headers: csrfHeaders() },
  );
}

export function getCountryWatchlistStatus(
  countrySlug: string,
): Promise<WatchlistStatusResponse> {
  return apiGet<WatchlistStatusResponse>(
    `/api/v1/countries/${countrySlug}/watchlist-status`,
    { headers: csrfHeaders() },
  );
}

export const watchlistsApi = {
  listWatchlist,
  addCountryToWatchlist,
  removeCountryFromWatchlist,
  updateWatchlistPreferences,
  getCountryWatchlistStatus,
};
