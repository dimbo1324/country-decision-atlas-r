import type { components } from "@country-decision-atlas/contracts/generated/types";

import { DEFAULT_LOCALE } from "../lib/locale";
import { apiGet, queryString } from "./http";

export type LocaleCode = components["schemas"]["LocaleCode"];
export type CountryListResponse = components["schemas"]["CountryListResponse"];
export type CountryReadModelResponse =
  components["schemas"]["CountryReadModelResponse"];

type ListCountriesParams = {
  locale?: LocaleCode;
  limit?: number;
  offset?: number;
};

export function listCountries(
  params: ListCountriesParams = {},
): Promise<CountryListResponse> {
  return apiGet<CountryListResponse>(
    `/api/v1/countries${queryString({
      locale: params.locale ?? DEFAULT_LOCALE,
      limit: params.limit,
      offset: params.offset,
    })}`,
  );
}

export function getCountryCard(
  countrySlug: string,
  locale: LocaleCode = DEFAULT_LOCALE,
): Promise<CountryReadModelResponse> {
  return apiGet<CountryReadModelResponse>(
    `/api/v1/countries/${countrySlug}/card${queryString({ locale })}`,
  );
}

export const countriesApi = {
  listCountries,
  getCountryCard,
};
