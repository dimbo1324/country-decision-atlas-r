import { RadioCards } from "@country-decision-atlas/ui";
import type { DecisionWizardOption } from "./decision-wizard-labels";

type DecisionWizardStepProps<T extends string> = {
  label: string;
  value: T;
  options: Array<DecisionWizardOption<T>>;
  testId: string;
  onChange: (value: T) => void;
};

export function DecisionWizardStep<T extends string>({
  label,
  value,
  options,
  testId,
  onChange,
}: DecisionWizardStepProps<T>) {
  return (
    <div
      className="flex flex-col gap-2"
      data-testid={testId}
    >
      <span className="font-mono text-c3 text-[10px] tracking-[0.2em] uppercase">
        {label}
      </span>
      <RadioCards
        name={testId}
        value={value}
        onChange={(next) => onChange(next as T)}
        options={options}
      />
    </div>
  );
}
