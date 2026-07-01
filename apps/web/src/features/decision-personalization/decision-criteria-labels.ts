export const DECISION_CRITERIA_LABELS = {
  legalization_score: "Легализация",
  long_term_status_score: "Долгосрочный статус",
  cost_of_living_score: "Стоимость жизни",
  safety_score: "Безопасность",
  business_score: "Бизнес",
  legal_stability_score: "Правовая стабильность",
  source_quality_score: "Качество источников",
} as const;

export type DecisionCriterion = keyof typeof DECISION_CRITERIA_LABELS;

export const DECISION_CRITERIA_ORDER: DecisionCriterion[] = [
  "legalization_score",
  "long_term_status_score",
  "cost_of_living_score",
  "safety_score",
  "business_score",
  "legal_stability_score",
  "source_quality_score",
];

export const DEFAULT_DECISION_WEIGHTS: Record<DecisionCriterion, number> = {
  legalization_score: 20,
  long_term_status_score: 15,
  cost_of_living_score: 15,
  safety_score: 20,
  business_score: 10,
  legal_stability_score: 10,
  source_quality_score: 10,
};
