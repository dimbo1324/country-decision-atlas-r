import type { components } from "@country-decision-atlas/contracts/generated/types";

import { apiGet, queryString } from "./http";

export type CiiCountryComparisonResponse =
  components["schemas"]["CiiCountryComparisonResponse"];
export type ComparedCountry = components["schemas"]["ComparedCountry"];
export type ComparedMetric = components["schemas"]["ComparedMetric"];
export type ComparedMetricValue = components["schemas"]["ComparedMetricValue"];
export type ComparedScenario = components["schemas"]["ComparedScenario"];

type CompareCountriesParams = {
  countries: string[];
  scenario: string;
  locale?: string;
};

export function compareCountriesCii(
  params: CompareCountriesParams,
): Promise<CiiCountryComparisonResponse> {
  return apiGet<CiiCountryComparisonResponse>(
    `/api/v1/countries/compare${queryString({
      countries: params.countries.join(","),
      scenario: params.scenario,
      locale: params.locale ?? "en",
    })}`,
  );
}

export const ciiApi = {
  compareCountriesCii,
};
