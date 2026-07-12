import createClient from "openapi-fetch";
import type { paths } from "@country-decision-atlas/contracts/generated/types";
import { API_BASE_URL, API_TIMEOUT_MS } from "../config/env";
import type { ApiErrorResponse } from "./http";

/** Typed client generated from contracts/openapi.yaml. This is the
 * openapi-fetch counterpart to the hand-rolled `http.ts` wrapper — new
 * domain query modules (see `entities/*`) use this one; the existing
 * `shared/api/*` modules keep using `http.ts` and migrate over gradually,
 * per the frontend plan's own "postepenno" wording, not in one pass. */
export const apiClient = createClient<paths>({
  baseUrl: API_BASE_URL,
  credentials: "include",
  cache: "no-store",
});

apiClient.use({
  onRequest({ request }) {
    if (request.signal) return request;
    return new Request(request, {
      signal: AbortSignal.timeout(API_TIMEOUT_MS),
    });
  },
});

/** openapi-fetch resolves to `{ data, error }` rather than throwing.
 * TanStack Query (and the rest of the app's error-handling, via
 * `isApiError`) expects a thrown `ApiErrorResponse` — this bridges the two
 * so a `queryFn` can just be `() => unwrap(apiClient.GET(...))`. */
export async function unwrap<T>(
  promise: Promise<{ data?: T; error?: unknown }>,
): Promise<T> {
  const { data, error } = await promise;
  if (error) {
    throw error as ApiErrorResponse;
  }
  return data as T;
}
