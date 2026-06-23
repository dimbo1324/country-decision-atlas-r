import type { components } from "@country-decision-atlas/contracts/generated/types";

import { DEFAULT_LOCALE } from "../lib/locale";
import { apiGet, queryString } from "./http";
import type { LocaleCode } from "./countries";

export type ScenarioListResponse = components["schemas"]["ScenarioListResponse"];

type ListScenariosParams = {
  locale?: LocaleCode;
  limit?: number;
  offset?: number;
};

export function listScenarios(
  params: ListScenariosParams = {},
): Promise<ScenarioListResponse> {
  return apiGet<ScenarioListResponse>(
    `/api/v1/scenarios${queryString({
      locale: params.locale ?? DEFAULT_LOCALE,
      limit: params.limit,
      offset: params.offset,
    })}`,
  );
}

export const scenariosApi = {
  listScenarios,
};
