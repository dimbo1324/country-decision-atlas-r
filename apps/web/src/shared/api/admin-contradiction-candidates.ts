import type { components } from "@country-decision-atlas/contracts/generated/types";
import { csrfHeaders } from "../auth/session";
import { apiGet, apiPatch } from "./http";

export type ContradictionCandidate =
  components["schemas"]["ContradictionCandidate"];
export type ContradictionCandidateListResponse =
  components["schemas"]["ContradictionCandidateListResponse"];
export type ContradictionCandidateStatusUpdateRequest =
  components["schemas"]["ContradictionCandidateStatusUpdateRequest"];

export function listAdminContradictionCandidates(
  status?: string,
): Promise<ContradictionCandidateListResponse> {
  const query = status ? `?status=${status}` : "";
  return apiGet<ContradictionCandidateListResponse>(
    `/api/v1/admin/contradiction-candidates${query}`,
    { headers: csrfHeaders() },
  );
}

export function updateContradictionCandidateStatus(
  candidateId: string,
  payload: ContradictionCandidateStatusUpdateRequest,
): Promise<ContradictionCandidate> {
  return apiPatch<
    ContradictionCandidate,
    ContradictionCandidateStatusUpdateRequest
  >(`/api/v1/admin/contradiction-candidates/${candidateId}/status`, payload, {
    headers: csrfHeaders(),
  });
}

export const adminContradictionCandidatesApi = {
  listAdminContradictionCandidates,
  updateContradictionCandidateStatus,
};
