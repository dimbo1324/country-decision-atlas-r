import type { components } from "@country-decision-atlas/contracts/generated/types";

import { apiPost } from "./http";

export type DecisionRunRequest = components["schemas"]["DecisionRunRequest"];
export type DecisionRunResponse = components["schemas"]["DecisionRunResponse"];

export function runDecision(payload: DecisionRunRequest): Promise<DecisionRunResponse> {
  return apiPost<DecisionRunResponse, DecisionRunRequest>(
    "/api/v1/decision/run",
    payload,
  );
}

export const decisionApi = {
  runDecision,
};
