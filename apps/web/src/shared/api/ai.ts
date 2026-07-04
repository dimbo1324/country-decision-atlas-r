import type { components } from "@country-decision-atlas/contracts/generated/types";

import { DEFAULT_LOCALE } from "../lib/locale";
import { apiPost } from "./http";

type LocaleCode = components["schemas"]["LocaleCode"];
export type AIAskRequest = components["schemas"]["AIAskRequest"];
export type AIAskResponse = components["schemas"]["AIAskResponse"];
export type AIExplainNumberRequest =
  components["schemas"]["AIExplainNumberRequest"];
export type AIExplainNumberResponse =
  components["schemas"]["AIExplainNumberResponse"];
export type AIDecisionIntentRequest =
  components["schemas"]["AIDecisionIntentRequest"];
export type AIDecisionIntentResponse =
  components["schemas"]["AIDecisionIntentResponse"];
export type AICitation = components["schemas"]["AICitation"];

export function askAI(payload: AIAskRequest): Promise<AIAskResponse> {
  return apiPost<AIAskResponse, AIAskRequest>("/api/v1/ai/ask", {
    ...payload,
    locale: payload.locale ?? DEFAULT_LOCALE,
  });
}

export function explainNumber(
  payload: AIExplainNumberRequest,
): Promise<AIExplainNumberResponse> {
  return apiPost<AIExplainNumberResponse, AIExplainNumberRequest>(
    "/api/v1/ai/explain-number",
    {
      ...payload,
      locale: (payload.locale ?? DEFAULT_LOCALE) as LocaleCode,
    },
  );
}

export function parseDecisionIntent(
  payload: AIDecisionIntentRequest,
): Promise<AIDecisionIntentResponse> {
  return apiPost<AIDecisionIntentResponse, AIDecisionIntentRequest>(
    "/api/v1/ai/decision-intent",
    {
      ...payload,
      locale: payload.locale ?? DEFAULT_LOCALE,
    },
  );
}

export const aiApi = {
  askAI,
  explainNumber,
  parseDecisionIntent,
};
