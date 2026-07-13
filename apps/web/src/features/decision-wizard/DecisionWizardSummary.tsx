import { Badge } from "@country-decision-atlas/ui";
import type { DecisionWizardRecommendation } from "../../shared/api/decision";

type DecisionWizardSummaryProps = {
  recommendation: DecisionWizardRecommendation;
  labels: {
    confidence: string;
    scenario: string;
    persona: string;
    noPersona: string;
    explanation: string;
    warnings: string;
    manualNote: string;
    warningLabels: Record<string, string>;
  };
};

export function DecisionWizardSummary({
  recommendation,
  labels,
}: DecisionWizardSummaryProps) {
  return (
    <div
      className="border-warm flex flex-col gap-4 border-t pt-4"
      data-testid="decision-wizard-result"
    >
      <div className="flex flex-wrap items-center gap-3">
        <span data-testid="decision-wizard-confidence">
          <Badge variant="trust">
            {labels.confidence}: {recommendation.confidence}
          </Badge>
        </span>
        <span className="text-c2 text-sm">
          {labels.scenario}:{" "}
          <strong className="text-c1">
            {recommendation.recommended_scenario_slug}
          </strong>
        </span>
        <span className="text-c2 text-sm">
          {labels.persona}:{" "}
          <strong className="text-c1">
            {recommendation.recommended_persona_slug ?? labels.noPersona}
          </strong>
        </span>
      </div>
      <div className="flex flex-col gap-2">
        <strong className="text-c2 text-sm">{labels.explanation}</strong>
        <ul
          className="text-c3 flex flex-col gap-1 text-sm"
          data-testid="decision-wizard-explanation"
        >
          {recommendation.explanation.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </div>
      {recommendation.warnings.length > 0 && (
        <div className="flex flex-col gap-2">
          <strong className="text-c2 text-sm">{labels.warnings}</strong>
          <ul
            className="flex flex-col gap-1"
            data-testid="decision-wizard-warnings"
          >
            {recommendation.warnings.map((warning) => (
              <li
                key={warning}
                className="text-terra3 text-sm"
              >
                {labels.warningLabels[warning] ?? warning}
              </li>
            ))}
          </ul>
        </div>
      )}
      <p
        className="text-c4 text-xs"
        data-testid="decision-wizard-manual-note"
      >
        {labels.manualNote}
      </p>
    </div>
  );
}
