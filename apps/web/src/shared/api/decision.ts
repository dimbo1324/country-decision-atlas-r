import type { components } from "@country-decision-atlas/contracts/generated/types";

import { apiPost } from "./http";

export type DecisionRunRequest = components["schemas"]["DecisionRunRequest"];
export type DecisionRunResponse = components["schemas"]["DecisionRunResponse"];
export type DecisionPersonalizationResponse =
  components["schemas"]["DecisionPersonalizationResponse"];
export type DecisionWeightItem = components["schemas"]["DecisionWeightItem"];
export type DecisionWizardAnswers = components["schemas"]["DecisionWizardAnswers"];
export type DecisionWizardRecommendation =
  components["schemas"]["DecisionWizardRecommendation"];

export function runDecision(payload: DecisionRunRequest): Promise<DecisionRunResponse> {
  return apiPost<DecisionRunResponse, DecisionRunRequest>(
    "/api/v1/decision/run",
    payload,
  );
}

export function resolveWizard(
  payload: DecisionWizardAnswers,
): Promise<DecisionWizardRecommendation> {
  return apiPost<DecisionWizardRecommendation, DecisionWizardAnswers>(
    "/api/v1/decision/wizard/resolve",
    payload,
  );
}

export const decisionApi = {
  runDecision,
  resolveWizard,
};
