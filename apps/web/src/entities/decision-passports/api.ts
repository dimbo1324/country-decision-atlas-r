import { useMutation } from "@tanstack/react-query";
import { decisionPassportsApi } from "../../shared/api/decision-passports";

export function useCreateDecisionPassportMutation() {
  return useMutation({
    mutationFn: decisionPassportsApi.createDecisionPassport,
  });
}

/** Plain async fn, not a `queryOptions` factory: the public token page is a
 * one-shot server `await`, not a client-side query. */
export const getPublicPassport = decisionPassportsApi.getDecisionPassport;
