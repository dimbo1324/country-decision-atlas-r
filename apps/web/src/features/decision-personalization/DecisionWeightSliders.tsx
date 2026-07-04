import {
  DECISION_CRITERIA_ORDER,
  type DecisionCriterion,
} from "./decision-criteria-labels";
import { DecisionWeightSlider } from "./DecisionWeightSlider";
import { DecisionWeightSummary } from "./DecisionWeightSummary";

type DecisionWeightSlidersProps = {
  weights: Record<DecisionCriterion, number>;
  onChange: (criterion: DecisionCriterion, value: number) => void;
  onReset: () => void;
};

export function DecisionWeightSliders({
  weights,
  onChange,
  onReset,
}: DecisionWeightSlidersProps) {
  const sum = DECISION_CRITERIA_ORDER.reduce(
    (total, criterion) => total + weights[criterion],
    0,
  );

  return (
    <details
      className="decisionPersonalizationPanel"
      data-testid="decision-weights-panel"
    >
      <summary>Настроить приоритеты</summary>
      <p className="formHint">
        Приоритеты влияют только на текущий расчёт и не меняют базовую
        методологию.
      </p>
      {DECISION_CRITERIA_ORDER.map((criterion) => (
        <DecisionWeightSlider
          key={criterion}
          criterion={criterion}
          value={weights[criterion]}
          onChange={onChange}
        />
      ))}
      <DecisionWeightSummary sum={sum} />
      <button
        type="button"
        className="runButton"
        onClick={onReset}
        data-testid="decision-weights-reset"
      >
        Сбросить
      </button>
    </details>
  );
}
