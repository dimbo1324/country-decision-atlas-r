import Link from "next/link";
import type { DecisionRunResponse } from "../../shared/api/decision";
import type { SupportedLocale } from "../../shared/lib/locale";
import { routes } from "../../shared/lib/routes";
import { ConfidenceBadge } from "../../shared/ui/ConfidenceBadge";
import { formatScore } from "../../shared/lib/format";
import { DecisionBreakdown } from "./DecisionBreakdown";
import { DecisionSources } from "./DecisionSources";
import { DecisionWarnings } from "./DecisionWarnings";

type DecisionCountryResult = DecisionRunResponse["results"][number];

type DecisionResultCardProps = {
  result: DecisionCountryResult;
  locale: SupportedLocale;
};

export function DecisionResultCard({ result, locale }: DecisionResultCardProps) {
  return (
    <div className="resultCard">
      <div className="resultCardHeader">
        <span className="resultRank" aria-label={`Rank ${result.rank}`}>
          #{result.rank}
        </span>
        <span className="resultCountryName">{result.country.name}</span>
        <span className="resultScore">{formatScore(result.score)}</span>
        <span className="metaChip">{result.score_label}</span>
        {result.confidence && <ConfidenceBadge confidence={result.confidence} />}
      </div>

      {result.summary && <p className="resultSummary">{result.summary}</p>}

      {result.strengths.length > 0 && (
        <div className="resultSection resultSectionPositive">
          <h4 className="resultSectionTitle">Strengths</h4>
          <ul className="pointsList pointsListPositive">
            {result.strengths.map((s, i) => (
              <li key={i}>{s.message}</li>
            ))}
          </ul>
        </div>
      )}

      {result.weaknesses.length > 0 && (
        <div className="resultSection resultSectionNegative">
          <h4 className="resultSectionTitle">Weaknesses</h4>
          <ul className="pointsList pointsListNegative">
            {result.weaknesses.map((w, i) => (
              <li key={i}>{w.message}</li>
            ))}
          </ul>
        </div>
      )}

      {result.risk_warnings.length > 0 && (
        <div className="resultSection resultSectionRisk">
          <h4 className="resultSectionTitle">Risk warnings</h4>
          <DecisionWarnings warnings={result.risk_warnings} />
        </div>
      )}

      {result.breakdown.length > 0 && (
        <div className="resultSection">
          <h4 className="resultSectionTitle">Score breakdown</h4>
          <DecisionBreakdown breakdown={result.breakdown} />
        </div>
      )}

      <div className="resultSection">
        <h4 className="resultSectionTitle">Evidence sources</h4>
        <DecisionSources sources={result.sources} />
      </div>

      <div className="entityLinkRow">
        <Link
          href={routes.countryWithLocale(result.country.slug, locale)}
          className="internalLink"
        >
          Open country card →
        </Link>
      </div>
    </div>
  );
}
