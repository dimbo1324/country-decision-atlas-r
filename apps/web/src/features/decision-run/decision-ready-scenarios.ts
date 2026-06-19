export const DECISION_READY_SCENARIO_SLUGS = [
  "relocation_residence",
  "permanent_residence_citizenship",
  "low_budget_living",
  "business_self_employment",
  "safety_political_risk",
] as const;

export function isDecisionReadyScenario(slug: string): boolean {
  return DECISION_READY_SCENARIO_SLUGS.includes(
    slug as (typeof DECISION_READY_SCENARIO_SLUGS)[number],
  );
}
