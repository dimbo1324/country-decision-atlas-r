import type { components } from "@country-decision-atlas/contracts/generated/types";

import { apiGet, queryString } from "./http";
import type { LocaleCode } from "./countries";
import type { EvidenceListResponse } from "./evidence";

export type LegalSignalListResponse =
  components["schemas"]["LegalSignalDetailListResponse"];
export type LegalSignalTimelineResponse =
  components["schemas"]["LegalSignalTimelineResponse"];
export type LegalSignalTimelineEvent =
  components["schemas"]["LegalSignalTimelineEvent"];
export type TimelineYearGroup = components["schemas"]["TimelineYearGroup"];

type ListLegalSignalsParams = {
  locale?: LocaleCode;
  countrySlug?: string;
  signalType?: string;
  impactDirection?: string;
  impactLevel?: string;
  status?: "published" | "archived";
  sort?:
    | "published_date"
    | "effective_date"
    | "impact_level"
    | "created_at"
    | "updated_at";
  order?: "asc" | "desc";
  limit?: number;
  offset?: number;
};

export type LegalSignalTimelineParams = {
  locale?: LocaleCode;
  countrySlug?: string;
  signalType?: string;
  impactDirection?: string;
  impactLevel?: string;
  affectedGroup?: string;
  yearFrom?: number;
  yearTo?: number;
  limit?: number;
  offset?: number;
};

export function listLegalSignals(
  params: ListLegalSignalsParams = {},
): Promise<LegalSignalListResponse> {
  return apiGet<LegalSignalListResponse>(
    `/api/v1/legal-signals${queryString({
      locale: params.locale ?? "en",
      country_slug: params.countrySlug,
      signal_type: params.signalType,
      impact_direction: params.impactDirection,
      impact_level: params.impactLevel,
      status: params.status,
      sort: params.sort,
      order: params.order,
      limit: params.limit,
      offset: params.offset,
    })}`,
  );
}

export function getLegalSignalEvidence(
  signalId: string,
  limit = 20,
): Promise<EvidenceListResponse> {
  return apiGet<EvidenceListResponse>(
    `/api/v1/legal-signals/${signalId}/evidence${queryString({ limit })}`,
  );
}

export function getLegalSignalTimeline(
  params: LegalSignalTimelineParams = {},
): Promise<LegalSignalTimelineResponse> {
  return apiGet<LegalSignalTimelineResponse>(
    `/api/v1/legal-signals/timeline${queryString({
      locale: params.locale ?? "en",
      country_slug: params.countrySlug,
      signal_type: params.signalType,
      impact_direction: params.impactDirection,
      impact_level: params.impactLevel,
      affected_group: params.affectedGroup,
      year_from: params.yearFrom,
      year_to: params.yearTo,
      limit: params.limit,
      offset: params.offset,
    })}`,
  );
}

export const legalSignalsApi = {
  listLegalSignals,
  getLegalSignalEvidence,
  getTimeline: getLegalSignalTimeline,
};
