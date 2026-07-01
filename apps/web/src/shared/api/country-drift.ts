import type { components } from "@country-decision-atlas/contracts/generated/types";

import { DEFAULT_LOCALE } from "../lib/locale";
import { apiGet, queryString } from "./http";

type LocaleCode = components["schemas"]["LocaleCode"];
export type CountryDriftResponse = components["schemas"]["CountryDriftResponse"];
export type CountryDriftSnapshot = components["schemas"]["CountryDriftSnapshot"];
export type CountryDriftHistoryItem = components["schemas"]["CountryDriftHistoryItem"];

export function getCountryDrift(
  countrySlug: string,
  locale: LocaleCode = DEFAULT_LOCALE,
): Promise<CountryDriftResponse> {
  return apiGet<CountryDriftResponse>(
    `/api/v1/countries/${countrySlug}/drift${queryString({ locale })}`,
  );
}

export const countryDriftApi = { getCountryDrift };
