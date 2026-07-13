import { queryOptions } from "@tanstack/react-query";
import { methodologyApi } from "../../shared/api/methodology";
import type { components } from "@country-decision-atlas/contracts/generated/types";

type LocaleCode = components["schemas"]["LocaleCode"];

export function methodologySectionsQuery(locale: LocaleCode) {
  return queryOptions({
    queryKey: ["methodology", "sections", locale] as const,
    queryFn: () => methodologyApi.listMethodologySections(locale),
    staleTime: 5 * 60_000,
  });
}

export function methodologySectionQuery(slug: string, locale: LocaleCode) {
  return queryOptions({
    queryKey: ["methodology", "section", slug, locale] as const,
    queryFn: () => methodologyApi.getMethodologySection(slug, locale),
    enabled: Boolean(slug),
    staleTime: 5 * 60_000,
  });
}

export function methodologyParametersQuery() {
  return queryOptions({
    queryKey: ["methodology", "parameters"] as const,
    queryFn: () => methodologyApi.listMethodologyParameters(),
    staleTime: 5 * 60_000,
  });
}
