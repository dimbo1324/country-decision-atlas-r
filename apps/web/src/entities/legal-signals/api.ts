import { queryOptions } from "@tanstack/react-query";
import { legalSignalsApi } from "../../shared/api/legal-signals";
import type { LocaleCode } from "../../shared/api/countries";

export type LegalSignalFilters = {
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

export function legalSignalListQuery(
  locale: LocaleCode,
  filters: LegalSignalFilters = {},
) {
  return queryOptions({
    queryKey: ["legal-signals", "list", locale, filters] as const,
    queryFn: () => legalSignalsApi.listLegalSignals({ locale, ...filters }),
    staleTime: 60_000,
  });
}

export type LegalSignalTimelineFilters = {
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

export function legalSignalTimelineQuery(
  locale: LocaleCode,
  filters: LegalSignalTimelineFilters = {},
) {
  return queryOptions({
    queryKey: ["legal-signals", "timeline", locale, filters] as const,
    queryFn: () => legalSignalsApi.getTimeline({ locale, ...filters }),
    staleTime: 60_000,
  });
}

export function legalSignalEvidenceQuery(signalId: string) {
  return queryOptions({
    queryKey: ["legal-signals", "evidence", signalId] as const,
    queryFn: () => legalSignalsApi.getLegalSignalEvidence(signalId),
    enabled: Boolean(signalId),
    staleTime: 60_000,
  });
}
