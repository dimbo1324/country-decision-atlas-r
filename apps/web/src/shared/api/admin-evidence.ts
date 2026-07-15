import type { components } from "@country-decision-atlas/contracts/generated/types";
import { csrfHeaders } from "../auth/session";
import { apiPost } from "./http";

export type SourceCreate = components["schemas"]["SourceCreate"];
export type EvidenceItemCreate = components["schemas"]["EvidenceItemCreate"];
export type LegalSignalCreate = components["schemas"]["LegalSignalCreate"];
export type AdminSourceResponse = components["schemas"]["AdminSourceResponse"];
export type AdminEvidenceItemResponse =
  components["schemas"]["AdminEvidenceItemResponse"];
export type AdminLegalSignalResponse =
  components["schemas"]["AdminLegalSignalResponse"];

export function createAdminSource(
  payload: SourceCreate,
): Promise<AdminSourceResponse> {
  return apiPost<AdminSourceResponse, SourceCreate>(
    "/api/v1/admin/sources",
    payload,
    { headers: csrfHeaders() },
  );
}

export function createAdminEvidenceItem(
  payload: EvidenceItemCreate,
): Promise<AdminEvidenceItemResponse> {
  return apiPost<AdminEvidenceItemResponse, EvidenceItemCreate>(
    "/api/v1/admin/evidence-items",
    payload,
    { headers: csrfHeaders() },
  );
}

export function createAdminLegalSignal(
  payload: LegalSignalCreate,
): Promise<AdminLegalSignalResponse> {
  return apiPost<AdminLegalSignalResponse, LegalSignalCreate>(
    "/api/v1/admin/legal-signals",
    payload,
    { headers: csrfHeaders() },
  );
}

export const adminEvidenceApi = {
  createAdminSource,
  createAdminEvidenceItem,
  createAdminLegalSignal,
};
