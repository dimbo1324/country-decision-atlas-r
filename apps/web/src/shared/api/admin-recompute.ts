import type { components } from "@country-decision-atlas/contracts/generated/types";
import { csrfHeaders } from "../auth/session";
import { apiPost } from "./http";

export type AdminRecomputeQueuedResponse =
  components["schemas"]["AdminRecomputeQueuedResponse"];
export type PlatformMetricsRecomputeRequest =
  components["schemas"]["PlatformMetricsRecomputeRequest"];
export type TrustRecomputeRequest =
  components["schemas"]["TrustRecomputeRequest"];
export type CountryDriftRecomputeRequest =
  components["schemas"]["CountryDriftRecomputeRequest"];

export function recomputeAllPlatformMetrics(): Promise<AdminRecomputeQueuedResponse> {
  return apiPost<AdminRecomputeQueuedResponse, PlatformMetricsRecomputeRequest>(
    "/api/v1/admin/platform-metrics/recompute",
    { dry_run: false },
    { headers: csrfHeaders() },
  );
}

export function recomputeAllTrust(): Promise<AdminRecomputeQueuedResponse> {
  return apiPost<AdminRecomputeQueuedResponse, TrustRecomputeRequest>(
    "/api/v1/admin/trust/recompute",
    { dry_run: false },
    { headers: csrfHeaders() },
  );
}

export function recomputeAllCountryDrift(): Promise<AdminRecomputeQueuedResponse> {
  return apiPost<AdminRecomputeQueuedResponse, CountryDriftRecomputeRequest>(
    "/api/v1/admin/country-drift/recompute",
    { dry_run: false, emit_events: true },
    { headers: csrfHeaders() },
  );
}

export const adminRecomputeApi = {
  recomputeAllPlatformMetrics,
  recomputeAllTrust,
  recomputeAllCountryDrift,
};
