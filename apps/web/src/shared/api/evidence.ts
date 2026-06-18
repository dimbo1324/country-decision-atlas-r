import type { components } from "@country-decision-atlas/contracts/generated/types";

import { apiGet, queryString } from "./http";

export type EvidenceItemListResponse =
  components["schemas"]["EvidenceItemListResponse"];

type ListEvidenceItemsParams = {
  countrySlug?: string;
  sourceId?: string;
  legalSignalId?: string;
  confidence?: "low" | "medium" | "high";
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

export const evidenceApi = {
  listEvidenceItems,
};
