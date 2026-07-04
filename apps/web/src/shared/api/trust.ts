import type { components } from "@country-decision-atlas/contracts/generated/types";

import { DEFAULT_LOCALE } from "../lib/locale";
import { apiGet, queryString } from "./http";

type LocaleCode = components["schemas"]["LocaleCode"];
export type CountryTrustResponse =
  components["schemas"]["CountryTrustResponse"];

export function getCountryTrust(
  countrySlug: string,
  locale: LocaleCode = DEFAULT_LOCALE,
): Promise<CountryTrustResponse> {
  return apiGet<CountryTrustResponse>(
    `/api/v1/countries/${countrySlug}/trust${queryString({ locale })}`,
  );
}

export const trustApi = { getCountryTrust };
