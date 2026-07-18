import { useAppLocale } from "../../shared/lib/useAppLocale";
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
  const locale = useAppLocale();
  const label = DECISION_CRITERIA_LABELS[locale][criterion];
  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between gap-2">
        <span className="text-c2 text-sm">{label}</span>
        <span className="font-display text-gold3 text-sm font-bold">
          {value}
        </span>
      </div>
      <input
        type="range"
        min={0}
        max={100}
        step={1}
        value={value}
        onChange={(e) => onChange(criterion, Number(e.target.value))}
        aria-label={label}
        data-testid={`decision-weight-slider-${criterion}`}
        className="accent-gold h-1 w-full cursor-pointer"
      />
    </div>
  );
}
