import type { components } from "@country-decision-atlas/contracts/generated/types";
import type { Confidence } from "@country-decision-atlas/ui";

import { apiGet, queryString } from "./http";

export type EvidenceItem = components["schemas"]["EvidenceItem"];
export type EvidenceItemListResponse =
  components["schemas"]["EvidenceItemListResponse"];
export type EvidenceListResponse =
  components["schemas"]["EvidenceListResponse"];

type ListEvidenceItemsParams = {
  countrySlug?: string;
  sourceId?: string;
  legalSignalId?: string;
  confidence?: Confidence;
  status?: "published" | "archived";
  sort?: "retrieved_at" | "created_at" | "confidence";
  order?: "asc" | "desc";
  limit?: number;
  offset?: number;
};

export function listEvidenceItems(
  params: ListEvidenceItemsParams = {},
): Promise<EvidenceItemListResponse> {
  return apiGet<EvidenceItemListResponse>(
    `/api/v1/evidence-items${queryString({
      country_slug: params.countrySlug,
      source_id: params.sourceId,
      legal_signal_id: params.legalSignalId,
      confidence: params.confidence,
      status: params.status,
      sort: params.sort,
      order: params.order,
      limit: params.limit,
      offset: params.offset,
    })}`,
  );
}

export function listEvidenceForLegalSignal(
  signalId: string,
  limit = 20,
): Promise<EvidenceListResponse> {
  return apiGet<EvidenceListResponse>(
    `/api/v1/legal-signals/${signalId}/evidence${queryString({ limit })}`,
  );
}

export function listEvidenceForSource(
  sourceId: string,
  limit = 50,
): Promise<EvidenceItemListResponse> {
  return apiGet<EvidenceItemListResponse>(
    `/api/v1/sources/${sourceId}/evidence${queryString({ limit })}`,
  );
}

export const evidenceApi = {
  listEvidenceItems,
  listEvidenceForLegalSignal,
  listEvidenceForSource,
};
