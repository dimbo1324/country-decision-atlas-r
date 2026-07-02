import type { components } from "@country-decision-atlas/contracts/generated/types";

import { DEFAULT_LOCALE } from "../lib/locale";
import { apiGet, queryString } from "./http";

type LocaleCode = components["schemas"]["LocaleCode"];
export type CountryPairCompatibilityResponse =
  components["schemas"]["CountryPairCompatibilityResponse"];
export type CountryPairCompatibilityListResponse =
  components["schemas"]["CountryPairCompatibilityListResponse"];

export function getCountryPair(
  originSlug: string,
  destinationSlug: string,
  locale: LocaleCode = DEFAULT_LOCALE,
): Promise<CountryPairCompatibilityResponse> {
  return apiGet<CountryPairCompatibilityResponse>(
    `/api/v1/country-pairs/${originSlug}/${destinationSlug}${queryString({ locale })}`,
  );
}

export function listDestinationCompatibility(
  originSlug: string,
  locale: LocaleCode = DEFAULT_LOCALE,
): Promise<CountryPairCompatibilityListResponse> {
  return apiGet<CountryPairCompatibilityListResponse>(
    `/api/v1/countries/${originSlug}/destination-compatibility${queryString({ locale })}`,
  );
}

export const countryPairsApi = {
  getCountryPair,
  listDestinationCompatibility,
};
