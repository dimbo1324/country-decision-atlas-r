import type { components } from "@country-decision-atlas/contracts/generated/types";
import type { Confidence } from "@country-decision-atlas/ui";

import { DEFAULT_API_LOCALE } from "../lib/locale";
import { apiGet, queryString } from "./http";
import type { LocaleCode } from "./countries";
import type { EvidenceItemListResponse } from "./evidence";

export type SourceListResponse = components["schemas"]["SourceListResponse"];

type ListSourcesParams = {
  locale?: LocaleCode;
  countrySlug?: string;
  sourceType?: string;
  language?: string;
  confidence?: Confidence;
  status?: "published" | "archived";
  sort?:
    | "title"
    | "created_at"
    | "published_at"
    | "last_checked_at"
    | "confidence";
  order?: "asc" | "desc";
  limit?: number;
  offset?: number;
};

export function listSources(
  params: ListSourcesParams = {},
): Promise<SourceListResponse> {
  return apiGet<SourceListResponse>(
    `/api/v1/sources${queryString({
      locale: params.locale ?? DEFAULT_API_LOCALE,
      country_slug: params.countrySlug,
      source_type: params.sourceType,
      language: params.language,
      confidence: params.confidence,
      status: params.status,
      sort: params.sort,
      order: params.order,
      limit: params.limit,
      offset: params.offset,
    })}`,
  );
}

export function getSourceEvidence(
  sourceId: string,
  limit = 50,
): Promise<EvidenceItemListResponse> {
  return apiGet<EvidenceItemListResponse>(
    `/api/v1/sources/${sourceId}/evidence${queryString({ limit })}`,
  );
}

export const sourcesApi = {
  listSources,
  getSourceEvidence,
};
