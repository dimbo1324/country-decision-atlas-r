import { queryOptions } from "@tanstack/react-query";
import { glossaryApi } from "../../shared/api/glossary";
import type { components } from "@country-decision-atlas/contracts/generated/types";

type LocaleCode = components["schemas"]["LocaleCode"];

export function glossaryTermsQuery(
  locale: LocaleCode,
  category?: string,
  q?: string,
) {
  return queryOptions({
    queryKey: ["glossary", "list", locale, category, q] as const,
    queryFn: () => glossaryApi.listGlossaryTerms(locale, category, q),
    staleTime: 5 * 60_000,
  });
}

export function glossaryTermQuery(slug: string, locale: LocaleCode) {
  return queryOptions({
    queryKey: ["glossary", "term", slug, locale] as const,
    queryFn: () => glossaryApi.getGlossaryTerm(slug, locale),
    enabled: Boolean(slug),
    staleTime: 5 * 60_000,
  });
}
