import type { components } from "@country-decision-atlas/contracts/generated/types";
import { csrfHeaders } from "../auth/session";
import { apiGet, apiPatch, apiPost } from "./http";

export type AIDraft = components["schemas"]["AIDraft"];
export type AIDraftListResponse = components["schemas"]["AIDraftListResponse"];
export type AIDraftGenerateSummaryRequest =
  components["schemas"]["AIDraftGenerateSummaryRequest"];
export type AIDraftStatusUpdateRequest =
  components["schemas"]["AIDraftStatusUpdateRequest"];

export function listAdminAiDrafts(
  status?: string,
): Promise<AIDraftListResponse> {
  const query = status ? `?status=${status}` : "";
  return apiGet<AIDraftListResponse>(`/api/v1/admin/ai/drafts${query}`, {
    headers: csrfHeaders(),
  });
}

export function generateAiDraftSummary(
  payload: AIDraftGenerateSummaryRequest,
): Promise<AIDraft> {
  return apiPost<AIDraft, AIDraftGenerateSummaryRequest>(
    "/api/v1/admin/ai/drafts/generate-summary",
    payload,
    { headers: csrfHeaders() },
  );
}

export function updateAiDraftStatus(
  draftId: string,
  payload: AIDraftStatusUpdateRequest,
): Promise<AIDraft> {
  return apiPatch<AIDraft, AIDraftStatusUpdateRequest>(
    `/api/v1/admin/ai/drafts/${draftId}/status`,
    payload,
    { headers: csrfHeaders() },
  );
}

export const adminAiDraftsApi = {
  listAdminAiDrafts,
  generateAiDraftSummary,
  updateAiDraftStatus,
};
