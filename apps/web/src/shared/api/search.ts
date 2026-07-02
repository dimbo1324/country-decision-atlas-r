import type { components } from "@country-decision-atlas/contracts/generated/types";

import { DEFAULT_LOCALE } from "../lib/locale";
import { apiGet, queryString } from "./http";

type LocaleCode = components["schemas"]["LocaleCode"];
export type SearchResultItem = components["schemas"]["SearchResultItem"];
export type SearchResponse = components["schemas"]["SearchResponse"];

type SearchParams = {
  q: string;
  locale?: LocaleCode;
  types?: string;
  countrySlug?: string;
  limit?: number;
  offset?: number;
};

export function search(params: SearchParams): Promise<SearchResponse> {
  return apiGet<SearchResponse>(
    `/api/v1/search${queryString({
      q: params.q,
      locale: params.locale ?? DEFAULT_LOCALE,
      types: params.types,
      country_slug: params.countrySlug,
      limit: params.limit,
      offset: params.offset,
    })}`,
  );
}

export const searchApi = {
  search,
};
