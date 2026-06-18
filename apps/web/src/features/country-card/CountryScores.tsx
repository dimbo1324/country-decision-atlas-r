import type { CountryReadModelResponse } from "../../shared/api/countries";
import { EmptyState } from "../../shared/ui/EmptyState";
import { formatScore } from "../../shared/lib/format";
import { ScoreBreakdown } from "./ScoreBreakdown";

type CountryScoresProps = {
  scores: CountryReadModelResponse["scores"];
};

export function CountryScores({ scores }: CountryScoresProps) {
  if (!scores || scores.length === 0) return <EmptyState />;

  return (
    <div className="scoreList">
      {scores.map((score) => (
        <div key={score.id} className="scoreCard">
          <div className="scoreCardHeader">
            <span className="scoreScenario">{score.scenario_title}</span>
            <span className="scoreBadge">{formatScore(score.score)}</span>
          </div>
          {score.confidence && (
            <span className="metaChip">Confidence: {score.confidence}</span>
          )}
          {score.explanation && (
            <p className="scoreExplanation">{score.explanation}</p>
          )}
          {score.breakdowns && score.breakdowns.length > 0 && (
            <ScoreBreakdown breakdowns={score.breakdowns} />
          )}
        </div>
      ))}
    </div>
  );
}
