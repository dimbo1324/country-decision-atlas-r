import { queryOptions, useMutation } from "@tanstack/react-query";
import type { components } from "@country-decision-atlas/contracts/generated/types";
import { decisionApi } from "../../shared/api/decision";
import { scenariosApi } from "../../shared/api/scenarios";
import { personasApi } from "../../shared/api/personas";
import { ciiApi } from "../../shared/api/cii";

type LocaleCode = components["schemas"]["LocaleCode"];

export function scenariosQuery(locale: LocaleCode) {
  return queryOptions({
    queryKey: ["scenarios", locale] as const,
    queryFn: () => scenariosApi.listScenarios({ locale }),
    staleTime: 5 * 60_000,
  });
}

export function personasQuery(locale: LocaleCode) {
  return queryOptions({
    queryKey: ["personas", locale] as const,
    queryFn: () => personasApi.listPersonas(locale),
    staleTime: 5 * 60_000,
  });
}

export function useRunDecisionMutation() {
  return useMutation({
    mutationFn: decisionApi.runDecision,
  });
}

export function useResolveWizardMutation() {
  return useMutation({
    mutationFn: decisionApi.resolveWizard,
  });
}

export function compareCiiQuery(params: {
  countries: string[];
  scenario: string;
  locale: string;
  persona?: string | null;
}) {
  return queryOptions({
    queryKey: ["cii", "compare", params] as const,
    queryFn: () => ciiApi.compareCountriesCii(params),
    enabled: params.countries.length >= 2 && Boolean(params.scenario),
    retry: false,
  });
}

export function matrixQuery(locale: LocaleCode) {
  return queryOptions({
    queryKey: ["cii", "matrix", locale] as const,
    queryFn: () => ciiApi.getMatrix({ scenarios: "all", locale }),
    staleTime: 60_000,
    retry: false,
  });
}
