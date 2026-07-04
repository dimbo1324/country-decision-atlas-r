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
      className="decisionWizardResult"
      data-testid="decision-wizard-result"
    >
      <div className="decisionWizardResultTop">
        <span
          className="badge"
          data-testid="decision-wizard-confidence"
        >
          {labels.confidence}: {recommendation.confidence}
        </span>
        <span>
          {labels.scenario}:{" "}
          <strong>{recommendation.recommended_scenario_slug}</strong>
        </span>
        <span>
          {labels.persona}:{" "}
          <strong>
            {recommendation.recommended_persona_slug ?? labels.noPersona}
          </strong>
        </span>
      </div>
      <div className="decisionWizardSummaryBlock">
        <strong>{labels.explanation}</strong>
        <ul
          className="pointsList"
          data-testid="decision-wizard-explanation"
        >
          {recommendation.explanation.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </div>
      {recommendation.warnings.length > 0 && (
        <div className="decisionWizardSummaryBlock">
          <strong>{labels.warnings}</strong>
          <ul
            className="warningsList"
            data-testid="decision-wizard-warnings"
          >
            {recommendation.warnings.map((warning) => (
              <li
                key={warning}
                className="warningItem"
              >
                {labels.warningLabels[warning] ?? warning}
              </li>
            ))}
          </ul>
        </div>
      )}
      <p
        className="formHint"
        data-testid="decision-wizard-manual-note"
      >
        {labels.manualNote}
      </p>
    </div>
  );
}
