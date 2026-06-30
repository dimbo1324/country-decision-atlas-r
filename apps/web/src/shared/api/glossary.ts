import type { components } from "@country-decision-atlas/contracts/generated/types";

import { DEFAULT_LOCALE } from "../lib/locale";
import { apiGet, queryString } from "./http";

type LocaleCode = components["schemas"]["LocaleCode"];
export type GlossaryTerm = components["schemas"]["GlossaryTerm"];
export type GlossaryListResponse = components["schemas"]["GlossaryListResponse"];

export function listGlossaryTerms(
  locale: LocaleCode = DEFAULT_LOCALE,
  category?: string,
  q?: string,
): Promise<GlossaryListResponse> {
  return apiGet<GlossaryListResponse>(
    `/api/v1/glossary${queryString({ locale, ...(category ? { category } : {}), ...(q ? { q } : {}) })}`,
  );
}

export function getGlossaryTerm(
  slug: string,
  locale: LocaleCode = DEFAULT_LOCALE,
): Promise<GlossaryTerm> {
  return apiGet<GlossaryTerm>(
    `/api/v1/glossary/${slug}${queryString({ locale })}`,
  );
}

export const glossaryApi = { listGlossaryTerms, getGlossaryTerm };
