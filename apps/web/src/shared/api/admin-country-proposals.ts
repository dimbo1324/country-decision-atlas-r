import type { components } from "@country-decision-atlas/contracts/generated/types";
import { csrfHeaders } from "../auth/session";
import { apiGet, apiPost } from "./http";

export type CountryProposal = components["schemas"]["CountryProposal"];
export type CountryProposalListResponse =
  components["schemas"]["CountryProposalListResponse"];
export type CountryProposalResponse =
  components["schemas"]["CountryProposalResponse"];
export type ModerationReasonPayload =
  components["schemas"]["ModerationReasonPayload"];
export type PublicationStatus = components["schemas"]["PublicationStatus"];

function listUrl(status?: PublicationStatus): string {
  const query = status ? `?status=${status}` : "";
  return `/api/v1/admin/country-proposals${query}`;
}

export function listAdminCountryProposals(
  status?: PublicationStatus,
): Promise<CountryProposalListResponse> {
  return apiGet<CountryProposalListResponse>(listUrl(status), {
    headers: csrfHeaders(),
  });
}

export function assignCountryProposalCurator(
  proposalId: string,
): Promise<CountryProposalResponse> {
  return apiPost<CountryProposalResponse, Record<string, never>>(
    `/api/v1/admin/country-proposals/${proposalId}/assign-curator`,
    {},
    { headers: csrfHeaders() },
  );
}

export function runCountryProposalReadinessCheck(
  proposalId: string,
): Promise<Record<string, unknown>> {
  return apiPost<Record<string, unknown>, Record<string, never>>(
    `/api/v1/admin/country-proposals/${proposalId}/readiness-check`,
    {},
    { headers: csrfHeaders() },
  );
}

export function publishCountryProposal(
  proposalId: string,
): Promise<CountryProposalResponse> {
  return apiPost<CountryProposalResponse, Record<string, never>>(
    `/api/v1/admin/country-proposals/${proposalId}/publish`,
    {},
    { headers: csrfHeaders() },
  );
}

export function rejectCountryProposal(
  proposalId: string,
  payload: ModerationReasonPayload,
): Promise<CountryProposalResponse> {
  return apiPost<CountryProposalResponse, ModerationReasonPayload>(
    `/api/v1/admin/country-proposals/${proposalId}/reject`,
    payload,
    { headers: csrfHeaders() },
  );
}

export function requestCountryProposalChanges(
  proposalId: string,
  payload: ModerationReasonPayload,
): Promise<CountryProposalResponse> {
  return apiPost<CountryProposalResponse, ModerationReasonPayload>(
    `/api/v1/admin/country-proposals/${proposalId}/request-changes`,
    payload,
    { headers: csrfHeaders() },
  );
}

export function archiveCountryProposal(
  proposalId: string,
): Promise<CountryProposalResponse> {
  return apiPost<CountryProposalResponse, Record<string, never>>(
    `/api/v1/admin/country-proposals/${proposalId}/archive`,
    {},
    { headers: csrfHeaders() },
  );
}

export const adminCountryProposalsApi = {
  listAdminCountryProposals,
  assignCountryProposalCurator,
  runCountryProposalReadinessCheck,
  publishCountryProposal,
  rejectCountryProposal,
  requestCountryProposalChanges,
  archiveCountryProposal,
};
