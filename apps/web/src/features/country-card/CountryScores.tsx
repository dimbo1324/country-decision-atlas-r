import type { CountryReadModelResponse } from "../../shared/api/countries";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ConfidenceBadge } from "../../shared/ui/ConfidenceBadge";
import { LocalizationBadge } from "../../shared/ui/LocalizationBadge";
import { formatScore } from "../../shared/lib/format";
import { ScoreBreakdown } from "./ScoreBreakdown";

type CountryScoresProps = {
  scores: CountryReadModelResponse["scores"];
  sources: CountryReadModelResponse["sources"];
};

export function CountryScores({ scores, sources }: CountryScoresProps) {
  const sourcesById = new Map(sources.map((s) => [s.id, s]));

  if (!scores || scores.length === 0) {
    return <EmptyState message="Оценки сценариев отсутствуют." />;
  }

  return (
    <div className="scoreList">
      {scores.map((score) => (
        <div
          key={score.id}
          className="scoreCard"
        >
          <div className="scoreCardHeader">
            <span className="scoreScenario">{score.scenario_title}</span>
            <span className="scoreBadge">{formatScore(score.score)}</span>
            <LocalizationBadge
              localization={score.localization}
              compact
            />
          </div>
          {score.confidence && (
            <ConfidenceBadge confidence={score.confidence} />
          )}
          {score.explanation && (
            <p className="scoreExplanation">{score.explanation}</p>
          )}
          {score.breakdowns && score.breakdowns.length > 0 && (
            <details className="breakdownDetails">
              <summary className="breakdownSummaryToggle">
                Разбор оценки
              </summary>
              <ScoreBreakdown
                breakdowns={score.breakdowns}
                sourcesById={sourcesById}
              />
            </details>
          )}
        </div>
      ))}
    </div>
  );
}
