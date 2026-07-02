import Link from "next/link";
import type { DecisionRunResponse } from "../../shared/api/decision";
import type { SupportedLocale } from "../../shared/lib/locale";
import { routes } from "../../shared/lib/routes";
import { ConfidenceBadge } from "../../shared/ui/ConfidenceBadge";
import { LocalizationBadge } from "../../shared/ui/LocalizationBadge";
import { formatScore } from "../../shared/lib/format";
import { DecisionBreakdown } from "./DecisionBreakdown";
import { DecisionCountryTrustBadge } from "./DecisionCountryTrustBadge";
import { DecisionSources } from "./DecisionSources";
import { DecisionWarnings } from "./DecisionWarnings";

type DecisionCountryResult = DecisionRunResponse["results"][number];
type OriginContextStatus = DecisionRunResponse["origin_context_status"];

type DecisionResultCardProps = {
  result: DecisionCountryResult;
  locale: SupportedLocale;
  originContextStatus?: OriginContextStatus;
};

const COMPATIBILITY_LABELS: Record<string, string> = {
  favourable: "Благоприятно",
  mixed: "Смешанно",
  restrictive: "Ограничено",
  unknown: "Неизвестно",
};

export function DecisionResultCard({
  result,
  locale,
  originContextStatus,
}: DecisionResultCardProps) {
  return (
    <div className="resultCard">
      <div className="resultCardHeader">
        <span className="resultRank" aria-label={`Место ${result.rank}`}>
          #{result.rank}
        </span>
        <span className="resultCountryName">{result.country.name}</span>
        <span className="resultScore">{formatScore(result.score)}</span>
        <span className="metaChip">{result.score_label}</span>
        {result.confidence && <ConfidenceBadge confidence={result.confidence} />}
        <LocalizationBadge localization={result.localization} compact />
      </div>

      <DecisionCountryTrustBadge countrySlug={result.country.slug} locale={locale} />

      {result.summary && <p className="resultSummary">{result.summary}</p>}

      {result.persona_adjusted_score != null && (
        <div className="resultPersonaScores" data-testid="persona-adjusted-score">
          <span>Базовая оценка: {formatScore(result.score)}</span>
          <span>
            Оценка с учетом персоны: {formatScore(result.persona_adjusted_score)}
          </span>
        </div>
      )}

      {result.strengths.length > 0 && (
        <div className="resultSection resultSectionPositive">
          <h4 className="resultSectionTitle">Сильные стороны</h4>
          <ul className="pointsList pointsListPositive">
            {result.strengths.map((s) => (
              <li key={s.message}>{s.message}</li>
            ))}
          </ul>
        </div>
      )}

      {result.weaknesses.length > 0 && (
        <div className="resultSection resultSectionNegative">
          <h4 className="resultSectionTitle">Слабые стороны</h4>
          <ul className="pointsList pointsListNegative">
            {result.weaknesses.map((w) => (
              <li key={w.message}>{w.message}</li>
            ))}
          </ul>
        </div>
      )}

      {result.risk_warnings.length > 0 && (
        <div className="resultSection resultSectionRisk">
          <h4 className="resultSectionTitle">Риски</h4>
          <DecisionWarnings warnings={result.risk_warnings} />
        </div>
      )}

      {originContextStatus && originContextStatus !== "not_requested" && (
        <div className="resultSection" data-testid="origin-aware-context">
          <h4 className="resultSectionTitle">Контекст маршрута</h4>
          {result.country_pair_context ? (
            <div className="originPairContext" data-testid="origin-pair-context">
              <div className="metaRow">
                <span className="metaChip">
                  {COMPATIBILITY_LABELS[
                    result.country_pair_context.compatibility_label
                  ] ?? result.country_pair_context.compatibility_label}
                </span>
                <ConfidenceBadge confidence={result.country_pair_context.confidence} />
              </div>
              {result.country_pair_context.practical_summary && (
                <p className="resultSummary">
                  {result.country_pair_context.practical_summary}
                </p>
              )}
              {(result.country_pair_context.key_notes ?? []).length > 0 && (
                <ul className="pointsList">
                  {(result.country_pair_context.key_notes ?? []).map((note) => (
                    <li key={note.type}>{note.message}</li>
                  ))}
                </ul>
              )}
              <p className="formHint">Практическая совместимость</p>
            </div>
          ) : (
            <p className="formHint" data-testid="origin-pair-context-empty">
              Нет данных по маршруту происхождения
            </p>
          )}
        </div>
      )}

      {result.breakdown.length > 0 && (
        <div className="resultSection">
          <h4 className="resultSectionTitle">Разбор оценки</h4>
          <DecisionBreakdown breakdown={result.breakdown} />
        </div>
      )}

      <div className="resultSection">
        <h4 className="resultSectionTitle">Источники</h4>
        <DecisionSources sources={result.sources} />
      </div>

      <div className="entityLinkRow">
        <Link
          href={routes.countryWithLocale(result.country.slug, locale)}
          className="internalLink"
        >
          Карточка страны →
        </Link>
      </div>
    </div>
  );
}
