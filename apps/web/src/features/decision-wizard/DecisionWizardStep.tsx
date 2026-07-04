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
    <label className="formGroup">
      <span className="formLabel">{label}</span>
      <select
        className="formSelect"
        value={value}
        onChange={(event) => onChange(event.target.value as T)}
        data-testid={testId}
      >
        {options.map((option) => (
          <option
            key={option.value}
            value={option.value}
          >
            {option.label}
          </option>
        ))}
      </select>
    </label>
  );
}
