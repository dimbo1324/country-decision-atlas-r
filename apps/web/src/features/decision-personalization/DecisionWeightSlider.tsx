import {
  DECISION_CRITERIA_LABELS,
  type DecisionCriterion,
} from "./decision-criteria-labels";

type DecisionWeightSliderProps = {
  criterion: DecisionCriterion;
  value: number;
  onChange: (criterion: DecisionCriterion, value: number) => void;
};

export function DecisionWeightSlider({
  criterion,
  value,
  onChange,
}: DecisionWeightSliderProps) {
  return (
    <div className="decisionWeightSlider">
      <div className="decisionWeightSliderHeader">
        <span>{DECISION_CRITERIA_LABELS[criterion]}</span>
        <span>{value}</span>
      </div>
      <input
        type="range"
        min={0}
        max={100}
        step={1}
        value={value}
        onChange={(e) => onChange(criterion, Number(e.target.value))}
        aria-label={DECISION_CRITERIA_LABELS[criterion]}
        data-testid={`decision-weight-slider-${criterion}`}
      />
    </div>
  );
}
