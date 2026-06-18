import type { DecisionRunResponse } from "../../shared/api/decision";

type DecisionRiskWarning =
  DecisionRunResponse["results"][number]["risk_warnings"][number];

type DecisionWarningsProps = {
  warnings: DecisionRiskWarning[];
};

export function DecisionWarnings({ warnings }: DecisionWarningsProps) {
  if (warnings.length === 0) return null;

  return (
    <ul className="warningsList">
      {warnings.map((w, i) => (
        <li key={i} className="warningItem">
          <span className={`metaChip metaChipWarn`}>{w.level}</span>
          <span>{w.message}</span>
        </li>
      ))}
    </ul>
  );
}
