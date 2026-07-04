import type { DecisionRunResponse } from "../../shared/api/decision";
import { ConfidenceBadge } from "../../shared/ui/ConfidenceBadge";
import { DisclaimerNotice } from "../../shared/ui/DisclaimerNotice";
import { EmptyState } from "../../shared/ui/EmptyState";
import { formatScore } from "../../shared/lib/format";
import { DecisionResultCard } from "./DecisionResultCard";
import { DecisionPersonalizationSummary } from "../decision-personalization";

type DecisionResultsProps = {
  response: DecisionRunResponse;
};

export function DecisionResults({ response }: DecisionResultsProps) {
  const {
    scenario,
    origin_country,
    origin_context_status,
    results,
    meta,
    locale,
    applied_persona,
    ranking_mode,
    personalization,
  } = response;

  const winner = results[0] ?? null;
  const isFallback = locale.translation_status === "fallback";

  return (
    <div
      className="decisionResults"
      data-testid="decision-results"
    >
      {isFallback && (
        <div className="fallbackBanner">
          Русский перевод частично отсутствует. Показана английская
          fallback-версия.
        </div>
      )}

      <div className="decisionResultsMeta">
        <div className="resultMetaRow">
          <span>Сценарий:</span>
          <strong>{scenario.title}</strong>
        </div>
        <div className="resultMetaRow">
          <span>Отправление:</span>
          <strong>{origin_country ? origin_country.name : "Не указано"}</strong>
        </div>
        <div className="resultMetaRow">
          <span>Создано:</span>
          <span>{new Date(meta.generated_at).toLocaleString("ru")}</span>
        </div>
        <div className="resultMetaRow">
          <span>Перевод:</span>
          <span className="metaChip">{locale.translation_status}</span>
        </div>
      </div>

      {applied_persona && (
        <div
          className="decisionPersonaMeta"
          data-testid="decision-persona-meta"
        >
          <div className="resultMetaRow">
            <span>Рейтинг адаптирован под профиль:</span>
            <strong>{applied_persona.name}</strong>
          </div>
          <div className="resultMetaRow">
            <span>Режим ранжирования:</span>
            <span className="metaChip">{ranking_mode}</span>
          </div>
        </div>
      )}

      <DecisionPersonalizationSummary personalization={personalization} />

      {winner && (
        <div className="decisionWinnerBlock">
          <p className="decisionWinnerLabel">Рекомендуемый вариант</p>
          <div className="decisionWinnerHeader">
            <span className="decisionWinnerName">{winner.country.name}</span>
            <span className="decisionWinnerScore">
              {formatScore(winner.persona_adjusted_score ?? winner.score)}
            </span>
          </div>
          <div className="metaRow">
            <span className="metaChip">{winner.score_label}</span>
            {winner.confidence && (
              <ConfidenceBadge confidence={winner.confidence} />
            )}
          </div>
          {winner.summary && (
            <p className="decisionWinnerSummary">{winner.summary}</p>
          )}
        </div>
      )}

      {results.length === 0 ? (
        <EmptyState message="Результаты подбора не получены." />
      ) : (
        <div className="resultList">
          <h3 className="resultListTitle">Полный рейтинг</h3>
          {results.map((result) => (
            <DecisionResultCard
              key={result.country.id}
              result={result}
              locale={locale.resolved_locale}
              originContextStatus={origin_context_status}
            />
          ))}
        </div>
      )}

      <DisclaimerNotice />
    </div>
  );
}
