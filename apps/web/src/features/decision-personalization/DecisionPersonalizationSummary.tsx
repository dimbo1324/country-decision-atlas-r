import type { DecisionPersonalizationResponse } from "../../shared/api/decision";
import {
  DECISION_CRITERIA_LABELS,
  type DecisionCriterion,
} from "./decision-criteria-labels";

type DecisionPersonalizationSummaryProps = {
  personalization: DecisionPersonalizationResponse;
};

function labelFor(criterion: string): string {
  return criterion in DECISION_CRITERIA_LABELS
    ? DECISION_CRITERIA_LABELS[criterion as DecisionCriterion]
    : criterion;
}

export function DecisionPersonalizationSummary({
  personalization,
}: DecisionPersonalizationSummaryProps) {
  if (!personalization.custom_weights_applied) {
    return null;
  }

  const sortedWeights = [...(personalization.effective_weights ?? [])].sort(
    (a, b) => b.weight - a.weight,
  );
  const topWeights = sortedWeights.slice(0, 3);

  return (
    <div
      className="decisionPersonalizationResult"
      data-testid="decision-personalization-result"
    >
      <p>Результат адаптирован под ваши приоритеты</p>
      <div className="resultMetaRow">
        <span>Режим расчёта:</span>
        <span className="metaChip">{personalization.weight_mode}</span>
      </div>
      {personalization.persona_slug && (
        <div className="resultMetaRow">
          <span>Персона:</span>
          <strong>{personalization.persona_slug}</strong>
        </div>
      )}
      <p className="formLabel">Главные приоритеты</p>
      <ul>
        {topWeights.map((item) => (
          <li key={item.criterion}>
            {labelFor(item.criterion)}: {Math.round(item.weight * 100)}%
          </li>
        ))}
      </ul>
      <details className="decisionEffectiveWeights">
        <summary>Все приоритеты</summary>
        <ul>
          {sortedWeights.map((item) => (
            <li key={item.criterion}>
              {labelFor(item.criterion)}: {Math.round(item.weight * 100)}%
            </li>
          ))}
        </ul>
      </details>
    </div>
  );
}
