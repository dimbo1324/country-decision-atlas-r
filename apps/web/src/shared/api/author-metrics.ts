import type { components } from "@country-decision-atlas/contracts/generated/types";
import { csrfHeaders } from "../auth/session";
import { apiGet, apiPatch, apiPost, apiPut } from "./http";

export type MyAuthorMetricDefinition =
  components["schemas"]["MyAuthorMetricDefinition"];
export type MyAuthorMetricListResponse =
  components["schemas"]["MyAuthorMetricListResponse"];
export type CreateAuthorMetricRequest =
  components["schemas"]["CreateAuthorMetricRequest"];
export type UpdateAuthorMetricRequest =
  components["schemas"]["UpdateAuthorMetricRequest"];
export type SubmitAuthorMetricResponse =
  components["schemas"]["SubmitAuthorMetricResponse"];
export type ArchiveAuthorMetricResponse =
  components["schemas"]["ArchiveAuthorMetricResponse"];
export type AuthorMetricValueItem =
  components["schemas"]["AuthorMetricValueItem"];
export type AuthorMetricValueResponse =
  components["schemas"]["AuthorMetricValueResponse"];
export type AuthorMetricValueListResponse =
  components["schemas"]["AuthorMetricValueListResponse"];
export type BulkUpsertAuthorMetricValuesRequest =
  components["schemas"]["BulkUpsertAuthorMetricValuesRequest"];
export type ForkAuthorMetricRequest =
  components["schemas"]["ForkAuthorMetricRequest"];
export type PublicAuthorMetricListResponse =
  components["schemas"]["PublicAuthorMetricListResponse"];
export type AuthorReputationResponse =
  components["schemas"]["AuthorReputationResponse"];
export type CountryAuthorMetricsResponse =
  components["schemas"]["CountryAuthorMetricsResponse"];
export type AdminAuthorMetricDefinition =
  components["schemas"]["AdminAuthorMetricDefinition"];
export type AdminAuthorMetricListResponse =
  components["schemas"]["AdminAuthorMetricListResponse"];
export type ModerateAuthorMetricRequest =
  components["schemas"]["ModerateAuthorMetricRequest"];
export type ModerateAuthorMetricResponse =
  components["schemas"]["ModerateAuthorMetricResponse"];
export type PublicationStatus = components["schemas"]["PublicationStatus"];

export function listMyAuthorMetrics(): Promise<MyAuthorMetricListResponse> {
  return apiGet<MyAuthorMetricListResponse>("/api/v1/me/author-metrics", {
    headers: csrfHeaders(),
  });
}

export function getMyAuthorMetric(
  definitionId: string,
): Promise<MyAuthorMetricDefinition> {
  return apiGet<MyAuthorMetricDefinition>(
    `/api/v1/me/author-metrics/${definitionId}`,
    { headers: csrfHeaders() },
  );
}

export function createMyAuthorMetric(
  payload: CreateAuthorMetricRequest,
): Promise<MyAuthorMetricDefinition> {
  return apiPost<MyAuthorMetricDefinition, CreateAuthorMetricRequest>(
    "/api/v1/me/author-metrics",
    payload,
    { headers: csrfHeaders() },
  );
}

export function updateMyAuthorMetric(
  definitionId: string,
  payload: UpdateAuthorMetricRequest,
): Promise<MyAuthorMetricDefinition> {
  return apiPatch<MyAuthorMetricDefinition, UpdateAuthorMetricRequest>(
    `/api/v1/me/author-metrics/${definitionId}`,
    payload,
    { headers: csrfHeaders() },
  );
}

export function submitMyAuthorMetric(
  definitionId: string,
): Promise<SubmitAuthorMetricResponse> {
  return apiPost<SubmitAuthorMetricResponse, Record<string, never>>(
    `/api/v1/me/author-metrics/${definitionId}/submit`,
    {},
    { headers: csrfHeaders() },
  );
}

export function archiveMyAuthorMetric(
  definitionId: string,
): Promise<ArchiveAuthorMetricResponse> {
  return apiPost<ArchiveAuthorMetricResponse, Record<string, never>>(
    `/api/v1/me/author-metrics/${definitionId}/archive`,
    {},
    { headers: csrfHeaders() },
  );
}

export function listMyAuthorMetricValues(
  definitionId: string,
): Promise<AuthorMetricValueListResponse> {
  return apiGet<AuthorMetricValueListResponse>(
    `/api/v1/me/author-metrics/${definitionId}/values`,
    { headers: csrfHeaders() },
  );
}

export function bulkUpsertMyAuthorMetricValues(
  definitionId: string,
  items: AuthorMetricValueItem[],
): Promise<AuthorMetricValueListResponse> {
  return apiPut<
    AuthorMetricValueListResponse,
    BulkUpsertAuthorMetricValuesRequest
  >(
    `/api/v1/me/author-metrics/${definitionId}/values`,
    { items },
    { headers: csrfHeaders() },
  );
}

export function forkAuthorMetric(
  definitionId: string,
  slug: string,
): Promise<MyAuthorMetricDefinition> {
  return apiPost<MyAuthorMetricDefinition, ForkAuthorMetricRequest>(
    `/api/v1/author-metrics/${definitionId}/fork`,
    { slug },
    { headers: csrfHeaders() },
  );
}

export function listAuthorPublicMetrics(
  userId: string,
): Promise<PublicAuthorMetricListResponse> {
  return apiGet<PublicAuthorMetricListResponse>(
    `/api/v1/authors/${userId}/metrics`,
  );
}

export function getAuthorReputation(
  userId: string,
): Promise<AuthorReputationResponse> {
  return apiGet<AuthorReputationResponse>(
    `/api/v1/authors/${userId}/reputation`,
  );
}

export function listCountryAuthorMetrics(
  countrySlug: string,
): Promise<CountryAuthorMetricsResponse> {
  return apiGet<CountryAuthorMetricsResponse>(
    `/api/v1/countries/${countrySlug}/author-metrics`,
  );
}

export function listAdminAuthorMetrics(
  status?: PublicationStatus,
): Promise<AdminAuthorMetricListResponse> {
  const query = status ? `?status=${status}` : "";
  return apiGet<AdminAuthorMetricListResponse>(
    `/api/v1/admin/author-metrics${query}`,
    { headers: csrfHeaders() },
  );
}

export function approveAdminAuthorMetric(
  definitionId: string,
): Promise<ModerateAuthorMetricResponse> {
  return apiPost<ModerateAuthorMetricResponse, Record<string, never>>(
    `/api/v1/admin/author-metrics/${definitionId}/approve`,
    {},
    { headers: csrfHeaders() },
  );
}

export function rejectAdminAuthorMetric(
  definitionId: string,
  payload: ModerateAuthorMetricRequest,
): Promise<ModerateAuthorMetricResponse> {
  return apiPost<ModerateAuthorMetricResponse, ModerateAuthorMetricRequest>(
    `/api/v1/admin/author-metrics/${definitionId}/reject`,
    payload,
    { headers: csrfHeaders() },
  );
}

export const authorMetricsApi = {
  listMyAuthorMetrics,
  getMyAuthorMetric,
  createMyAuthorMetric,
  updateMyAuthorMetric,
  submitMyAuthorMetric,
  archiveMyAuthorMetric,
  listMyAuthorMetricValues,
  bulkUpsertMyAuthorMetricValues,
  forkAuthorMetric,
  listAuthorPublicMetrics,
  getAuthorReputation,
  listCountryAuthorMetrics,
  listAdminAuthorMetrics,
  approveAdminAuthorMetric,
  rejectAdminAuthorMetric,
};
