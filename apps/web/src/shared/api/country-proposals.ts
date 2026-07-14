import type { components } from "@country-decision-atlas/contracts/generated/types";
import { csrfHeaders } from "../auth/session";
import { apiGet, apiPatch, apiPost, apiPut } from "./http";

export type CountryProposal = components["schemas"]["CountryProposal"];
export type CountryProposalCreate =
  components["schemas"]["CountryProposalCreate"];
export type CountryProposalPatch =
  components["schemas"]["CountryProposalPatch"];
export type CountryProposalResponse =
  components["schemas"]["CountryProposalResponse"];
export type CountryProposalListResponse =
  components["schemas"]["CountryProposalListResponse"];
export type ContributorSourceCreate =
  components["schemas"]["ContributorSourceCreate"];
export type ContributorEvidenceItemCreate =
  components["schemas"]["ContributorEvidenceItemCreate"];
export type ContributorLegalSignalCreate =
  components["schemas"]["ContributorLegalSignalCreate"];
export type ContributorTimelineEventCreate =
  components["schemas"]["ContributorTimelineEventCreate"];
export type CountryMetricValueEntry =
  components["schemas"]["CountryMetricValueEntry"];
export type CountryCardUpsert = components["schemas"]["CountryCardUpsert"];
export type GenericItemResponse = components["schemas"]["GenericItemResponse"];

export function listMyCountryProposals(): Promise<CountryProposalListResponse> {
  return apiGet<CountryProposalListResponse>("/api/v1/me/country-proposals", {
    headers: csrfHeaders(),
  });
}

export function getMyCountryProposal(
  proposalId: string,
): Promise<CountryProposalResponse> {
  return apiGet<CountryProposalResponse>(
    `/api/v1/me/country-proposals/${proposalId}`,
    { headers: csrfHeaders() },
  );
}

export function createMyCountryProposal(
  payload: CountryProposalCreate,
): Promise<CountryProposalResponse> {
  return apiPost<CountryProposalResponse, CountryProposalCreate>(
    "/api/v1/me/country-proposals",
    payload,
    { headers: csrfHeaders() },
  );
}

export function patchMyCountryProposal(
  proposalId: string,
  payload: CountryProposalPatch,
): Promise<CountryProposalResponse> {
  return apiPatch<CountryProposalResponse, CountryProposalPatch>(
    `/api/v1/me/country-proposals/${proposalId}`,
    payload,
    { headers: csrfHeaders() },
  );
}

export function submitMyCountryProposal(
  proposalId: string,
): Promise<CountryProposalResponse> {
  return apiPost<CountryProposalResponse, Record<string, never>>(
    `/api/v1/me/country-proposals/${proposalId}/submit`,
    {},
    { headers: csrfHeaders() },
  );
}

export function upsertMyCountryProposalCard(
  proposalId: string,
  locale: string,
  payload: CountryCardUpsert,
): Promise<GenericItemResponse> {
  return apiPut<GenericItemResponse, CountryCardUpsert>(
    `/api/v1/me/country-proposals/${proposalId}/card/${locale}`,
    payload,
    { headers: csrfHeaders() },
  );
}

export function createMyCountryProposalSource(
  proposalId: string,
  payload: ContributorSourceCreate,
): Promise<GenericItemResponse> {
  return apiPost<GenericItemResponse, ContributorSourceCreate>(
    `/api/v1/me/country-proposals/${proposalId}/sources`,
    payload,
    { headers: csrfHeaders() },
  );
}

export function createMyCountryProposalEvidenceItem(
  proposalId: string,
  payload: ContributorEvidenceItemCreate,
): Promise<GenericItemResponse> {
  return apiPost<GenericItemResponse, ContributorEvidenceItemCreate>(
    `/api/v1/me/country-proposals/${proposalId}/evidence-items`,
    payload,
    { headers: csrfHeaders() },
  );
}

export function createMyCountryProposalLegalSignal(
  proposalId: string,
  payload: ContributorLegalSignalCreate,
): Promise<GenericItemResponse> {
  return apiPost<GenericItemResponse, ContributorLegalSignalCreate>(
    `/api/v1/me/country-proposals/${proposalId}/legal-signals`,
    payload,
    { headers: csrfHeaders() },
  );
}

export function createMyCountryProposalTimelineEvent(
  proposalId: string,
  payload: ContributorTimelineEventCreate,
): Promise<GenericItemResponse> {
  return apiPost<GenericItemResponse, ContributorTimelineEventCreate>(
    `/api/v1/me/country-proposals/${proposalId}/timeline-events`,
    payload,
    { headers: csrfHeaders() },
  );
}

export function upsertMyCountryProposalMetricValues(
  proposalId: string,
  values: CountryMetricValueEntry[],
): Promise<GenericItemResponse> {
  return apiPut<GenericItemResponse, { values: CountryMetricValueEntry[] }>(
    `/api/v1/me/country-proposals/${proposalId}/metric-values`,
    { values },
    { headers: csrfHeaders() },
  );
}

export const countryProposalsApi = {
  listMyCountryProposals,
  getMyCountryProposal,
  createMyCountryProposal,
  patchMyCountryProposal,
  submitMyCountryProposal,
  upsertMyCountryProposalCard,
  createMyCountryProposalSource,
  createMyCountryProposalEvidenceItem,
  createMyCountryProposalLegalSignal,
  createMyCountryProposalTimelineEvent,
  upsertMyCountryProposalMetricValues,
};
