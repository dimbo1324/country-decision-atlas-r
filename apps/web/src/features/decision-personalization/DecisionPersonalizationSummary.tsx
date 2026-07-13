import { Badge } from "@country-decision-atlas/ui";
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
      className="flex flex-col gap-3"
      data-testid="decision-personalization-result"
    >
      <p className="text-c2 text-sm">
        Результат адаптирован под ваши приоритеты
      </p>
      <div className="flex items-center gap-2">
        <span className="text-c4 text-xs">Режим расчёта:</span>
        <Badge variant="default">{personalization.weight_mode}</Badge>
      </div>
      {personalization.persona_slug && (
        <div className="flex items-center gap-2">
          <span className="text-c4 text-xs">Персона:</span>
          <strong className="text-c1 text-sm">
            {personalization.persona_slug}
          </strong>
        </div>
      )}
      <p className="font-mono text-c4 text-[9px] tracking-[0.2em] uppercase">
        Главные приоритеты
      </p>
      <ul className="text-c3 flex flex-col gap-1 text-sm">
        {topWeights.map((item) => (
          <li key={item.criterion}>
            {labelFor(item.criterion)}: {Math.round(item.weight * 100)}%
          </li>
        ))}
      </ul>
      <details>
        <summary className="font-mono text-c3 hover:text-gold cursor-pointer text-[9px] tracking-[0.15em] uppercase transition-colors duration-300">
          Все приоритеты
        </summary>
        <ul className="text-c3 mt-2 flex flex-col gap-1 text-sm">
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
