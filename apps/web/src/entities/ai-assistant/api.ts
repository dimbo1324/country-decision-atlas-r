import { useMutation } from "@tanstack/react-query";
import { aiApi } from "../../shared/api/ai";

export function useAskAIMutation() {
  return useMutation({
    mutationFn: aiApi.askAI,
  });
}

export function useExplainNumberMutation() {
  return useMutation({
    mutationFn: aiApi.explainNumber,
  });
}

export function useParseDecisionIntentMutation() {
  return useMutation({
    mutationFn: aiApi.parseDecisionIntent,
  });
}
