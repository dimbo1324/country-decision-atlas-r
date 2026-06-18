import type { components } from "@country-decision-atlas/contracts/generated/types";

import { apiGet, queryString } from "./http";
import type { LocaleCode } from "./countries";

export type LegalSignalListResponse =
  components["schemas"]["LegalSignalDetailListResponse"];

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

export const legalSignalsApi = {
  listLegalSignals,
};
