import type { SupportedLocale } from "../../shared/lib/locale";

export const DECISION_CRITERIA_LABELS_EN = {
  legalization_score: "Legalization",
  long_term_status_score: "Long-term status",
  cost_of_living_score: "Cost of living",
  safety_score: "Safety",
  business_score: "Business",
  legal_stability_score: "Legal stability",
  source_quality_score: "Source quality",
} as const;

export type DecisionCriterion = keyof typeof DECISION_CRITERIA_LABELS_EN;

export const DECISION_CRITERIA_LABELS: Record<
  SupportedLocale,
  Record<DecisionCriterion, string>
> = {
  en: DECISION_CRITERIA_LABELS_EN,
  ru: {
    legalization_score: "Легализация",
    long_term_status_score: "Долгосрочный статус",
    cost_of_living_score: "Стоимость жизни",
    safety_score: "Безопасность",
    business_score: "Бизнес",
    legal_stability_score: "Правовая стабильность",
    source_quality_score: "Качество источников",
  },
  es: {
    legalization_score: "Legalización",
    long_term_status_score: "Estatus a largo plazo",
    cost_of_living_score: "Costo de vida",
    safety_score: "Seguridad",
    business_score: "Negocios",
    legal_stability_score: "Estabilidad legal",
    source_quality_score: "Calidad de las fuentes",
  },
};

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
