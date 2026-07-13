import type { DecisionRunResponse } from "../../shared/api/decision";
import { ImpactLevelBadge } from "../../shared/ui/ImpactBadge";

type DecisionRiskWarning =
  DecisionRunResponse["results"][number]["risk_warnings"][number];

type DecisionWarningsProps = {
  warnings: DecisionRiskWarning[];
};

export function DecisionWarnings({ warnings }: DecisionWarningsProps) {
  if (warnings.length === 0) return null;

  return (
    <ul
      className="flex flex-col gap-2"
      role="list"
    >
      {warnings.map((w) => (
        <li
          key={`${w.level}-${w.message}`}
          className="flex items-start gap-2"
        >
          <ImpactLevelBadge level={w.level} />
          <span className="text-c3 text-sm">{w.message}</span>
        </li>
      ))}
    </ul>
  );
}
