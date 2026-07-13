import { Button } from "@country-decision-atlas/ui";
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
    <details data-testid="decision-weights-panel">
      <summary className="font-mono text-c3 hover:text-gold cursor-pointer text-[10px] tracking-[0.15em] uppercase transition-colors duration-300">
        Настроить приоритеты
      </summary>
      <div className="mt-4 flex flex-col gap-5">
        <p className="text-c4 text-xs">
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
        <Button
          variant="ghost"
          onClick={onReset}
          data-testid="decision-weights-reset"
        >
          Сбросить
        </Button>
      </div>
    </details>
  );
}
