import type { components } from "@country-decision-atlas/contracts/generated/types";

import { apiGet, apiPost } from "./http";

export type DecisionPassportCreateRequest =
  components["schemas"]["DecisionPassportCreateRequest"];
export type DecisionPassportCreateResponse =
  components["schemas"]["DecisionPassportCreateResponse"];
export type DecisionPassportResponse =
  components["schemas"]["DecisionPassportResponse"];

export function createDecisionPassport(
  payload: DecisionPassportCreateRequest,
): Promise<DecisionPassportCreateResponse> {
  return apiPost<DecisionPassportCreateResponse, DecisionPassportCreateRequest>(
    "/api/v1/decision/passports",
    payload,
  );
}

export function getDecisionPassport(token: string): Promise<DecisionPassportResponse> {
  return apiGet<DecisionPassportResponse>(`/api/v1/decision/passports/${token}`);
}

export const decisionPassportsApi = {
  createDecisionPassport,
  getDecisionPassport,
};
