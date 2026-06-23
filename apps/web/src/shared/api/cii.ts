import type { components } from "@country-decision-atlas/contracts/generated/types";

import { DEFAULT_LOCALE } from "../lib/locale";
import { apiGet, queryString } from "./http";

export type CiiCountryComparisonResponse =
  components["schemas"]["CiiCountryComparisonResponse"];
export type ComparedCountry = components["schemas"]["ComparedCountry"];
export type ComparedMetric = components["schemas"]["ComparedMetric"];
export type ComparedMetricValue = components["schemas"]["ComparedMetricValue"];
export type ComparedScenario = components["schemas"]["ComparedScenario"];
export type CompareMatrixResponse = components["schemas"]["CompareMatrixResponse"];
export type MatrixCountry = components["schemas"]["MatrixCountry"];
export type MatrixScenario = components["schemas"]["MatrixScenario"];
export type MatrixCell = components["schemas"]["MatrixCell"];

type CompareCountriesParams = {
  countries: string[];
  scenario: string;
  locale?: string;
};

type GetMatrixParams = {
  countries?: string[];
  scenarios?: string[] | "all";
  locale?: string;
};

export function compareCountriesCii(
  params: CompareCountriesParams,
): Promise<CiiCountryComparisonResponse> {
  return apiGet<CiiCountryComparisonResponse>(
    `/api/v1/countries/compare${queryString({
      countries: params.countries.join(","),
      scenario: params.scenario,
      locale: params.locale ?? DEFAULT_LOCALE,
    })}`,
  );
}

export function getMatrix(params: GetMatrixParams): Promise<CompareMatrixResponse> {
  const scenariosParam =
    params.scenarios === "all" || params.scenarios === undefined
      ? "all"
      : params.scenarios.join(",");
  return apiGet<CompareMatrixResponse>(
    `/api/v1/countries/matrix${queryString({
      countries: params.countries?.join(","),
      scenarios: scenariosParam,
      locale: params.locale ?? DEFAULT_LOCALE,
    })}`,
  );
}

export const ciiApi = {
  compareCountriesCii,
  getMatrix,
};
