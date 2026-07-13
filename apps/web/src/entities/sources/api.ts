import { queryOptions } from "@tanstack/react-query";
import { sourcesApi } from "../../shared/api/sources";
import { evidenceApi } from "../../shared/api/evidence";
import type { LocaleCode } from "../../shared/api/countries";

export type SourceFilters = {
  countrySlug?: string;
  sourceType?: string;
  language?: string;
  confidence?: "low" | "medium" | "high";
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

export function sourceListQuery(
  locale: LocaleCode,
  filters: SourceFilters = {},
) {
  return queryOptions({
    queryKey: ["sources", "list", locale, filters] as const,
    queryFn: () => sourcesApi.listSources({ locale, ...filters }),
    staleTime: 60_000,
  });
}

export function sourceEvidenceQuery(sourceId: string) {
  return queryOptions({
    queryKey: ["sources", "evidence", sourceId] as const,
    queryFn: () => evidenceApi.listEvidenceForSource(sourceId),
    enabled: Boolean(sourceId),
    staleTime: 60_000,
  });
}
