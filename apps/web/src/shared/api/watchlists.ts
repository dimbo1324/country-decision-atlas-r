import type { components } from "@country-decision-atlas/contracts/generated/types";
import { authHeaders } from "../auth/session";
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
    headers: authHeaders(),
  });
}

export function addCountryToWatchlist(
  countrySlug: string,
): Promise<WatchlistItem> {
  return apiPost<WatchlistItem, Record<string, never>>(
    `/api/v1/me/watchlist/countries/${countrySlug}`,
    {},
    { headers: authHeaders() },
  );
}

export function removeCountryFromWatchlist(countrySlug: string): Promise<void> {
  return apiDelete<void>(`/api/v1/me/watchlist/countries/${countrySlug}`, {
    headers: authHeaders(),
  });
}

export function updateWatchlistPreferences(
  countrySlug: string,
  payload: WatchlistPreferencesUpdate,
): Promise<WatchlistItem> {
  return apiPatch<WatchlistItem, WatchlistPreferencesUpdate>(
    `/api/v1/me/watchlist/countries/${countrySlug}`,
    payload,
    { headers: authHeaders() },
  );
}

export function getCountryWatchlistStatus(
  countrySlug: string,
): Promise<WatchlistStatusResponse> {
  return apiGet<WatchlistStatusResponse>(
    `/api/v1/countries/${countrySlug}/watchlist-status`,
    { headers: authHeaders() },
  );
}

export const watchlistsApi = {
  listWatchlist,
  addCountryToWatchlist,
  removeCountryFromWatchlist,
  updateWatchlistPreferences,
  getCountryWatchlistStatus,
};
