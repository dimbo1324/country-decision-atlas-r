import type { components } from "@country-decision-atlas/contracts/generated/types";
import type { LocaleCode } from "./countries";
import { apiGet, queryString } from "./http";

export type HomeOverviewResponse = components["schemas"]["HomeOverviewResponse"];
export type CountryOverviewCard = components["schemas"]["CountryOverviewCard"];
export type ScenarioWinner = components["schemas"]["ScenarioWinner"];
export type HomeMatrixPreview = components["schemas"]["HomeMatrixPreview"];
export type LatestLegalEvent = components["schemas"]["LatestLegalEvent"];
export type HomeKeyInsight = components["schemas"]["HomeKeyInsight"];

export function getHomeOverview(
  params: { locale?: LocaleCode } = {},
): Promise<HomeOverviewResponse> {
  return apiGet<HomeOverviewResponse>(
    `/api/v1/home/overview${queryString({ locale: params.locale ?? "en" })}`,
  );
}

export const homeApi = {
  getOverview: getHomeOverview,
};
