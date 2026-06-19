import type { DecisionRunResponse } from "../../shared/api/decision";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ConfidenceBadge } from "../../shared/ui/ConfidenceBadge";
import { formatScore } from "../../shared/lib/format";
import { DecisionResultCard } from "./DecisionResultCard";

type DecisionResultsProps = {
  response: DecisionRunResponse;
};

export function DecisionResults({ response }: DecisionResultsProps) {
  const { scenario, origin_country, results, meta, locale } = response;

  const winner = results[0] ?? null;
  const isFallback = locale.translation_status === "fallback";

  return (
    <div className="decisionResults" data-testid="decision-results">
      {isFallback && (
        <div className="fallbackBanner">
          {locale.requested_locale === "ru"
            ? "Русский перевод частично отсутствует. Показана английская fallback-версия."
            : "Translation content is missing. Showing fallback language content."}
        </div>
      )}

      <div className="decisionResultsMeta">
        <div className="resultMetaRow">
          <span>Scenario:</span>
          <strong>{scenario.title}</strong>
        </div>
        <div className="resultMetaRow">
          <span>Origin:</span>
          <strong>{origin_country.name}</strong>
        </div>
        <div className="resultMetaRow">
          <span>Generated:</span>
          <span>{new Date(meta.generated_at).toLocaleString("en")}</span>
        </div>
        <div className="resultMetaRow">
          <span>Translation:</span>
          <span className="metaChip">{locale.translation_status}</span>
        </div>
      </div>

      {winner && (
        <div className="decisionWinnerBlock">
          <p className="decisionWinnerLabel">Recommended first</p>
          <div className="decisionWinnerHeader">
            <span className="decisionWinnerName">{winner.country.name}</span>
            <span className="decisionWinnerScore">{formatScore(winner.score)}</span>
          </div>
          <div className="metaRow">
            <span className="metaChip">{winner.score_label}</span>
            {winner.confidence && <ConfidenceBadge confidence={winner.confidence} />}
          </div>
          {winner.summary && (
            <p className="decisionWinnerSummary">{winner.summary}</p>
          )}
        </div>
      )}

      {results.length === 0 ? (
        <EmptyState message="No decision results were returned." />
      ) : (
        <div className="resultList">
          <h3 className="resultListTitle">Full ranking</h3>
          {results.map((result) => (
            <DecisionResultCard key={result.country.id} result={result} locale={locale.resolved_locale} />
          ))}
        </div>
      )}
    </div>
  );
}
