import { Badge, Card, Kicker } from "@country-decision-atlas/ui";
import { Link } from "../../i18n/navigation";
import type { DecisionRunResponse } from "../../shared/api/decision";
import { ConfidenceBadge } from "../../shared/ui/ConfidenceBadge";
import { DisclaimerNotice } from "../../shared/ui/DisclaimerNotice";
import { EmptyState } from "../../shared/ui/EmptyState";
import { formatDateTime, formatScore } from "../../shared/lib/format";
import {
  asSupportedLocale,
  type SupportedLocale,
} from "../../shared/lib/locale";
import { ArrowNext } from "../../shared/ui/LinkArrow";
import { AIExplainNumberButton } from "../ai-assistant";
import { DecisionResultCard } from "./DecisionResultCard";
import { DecisionPersonalizationSummary } from "../decision-personalization";

type DecisionResultsProps = {
  response: DecisionRunResponse;
  /** The real interface locale, not `response.locale` (the backend's data
   * locale) -- passed as a prop rather than read via `useAppLocale()`
   * internally because this component renders from both a client tree
   * (`DecisionRunForm`) and a Server Component (the decision-passport
   * page), and hooks aren't available in the latter. */
  uiLocale: SupportedLocale;
};

export function DecisionResults({ response, uiLocale }: DecisionResultsProps) {
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
      className="flex flex-col gap-6"
      data-testid="decision-results"
    >
      {/* Screen-reader-only: DecisionResults re-renders in place on every
          recompute (weight/persona/candidate change), so a sighted user
          sees the update but nothing tells an AT user new results
          landed -- role="status" (implicit aria-live="polite") announces
          just the winner, not the whole results block, to avoid an overly
          verbose re-read of the entire ranking on every change. */}
      <p
        role="status"
        className="sr-only"
      >
        {winner
          ? `Результаты обновлены. Рекомендуем: ${winner.country.name}.`
          : "Результаты обновлены."}
      </p>

      {isFallback && (
        <p className="border-terra2/60 text-terra3 border px-4 py-3 text-sm">
          Русский перевод частично отсутствует. Показана английская
          fallback-версия.
        </p>
      )}

      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-2">
          <span className="text-c4 text-xs">Сценарий:</span>
          <strong className="text-c1 text-sm">{scenario.title}</strong>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-c4 text-xs">Отправление:</span>
          <strong className="text-c1 text-sm">
            {origin_country ? origin_country.name : "Не указано"}
          </strong>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-c4 text-xs">Создано:</span>
          <span className="text-c3 text-sm">
            {formatDateTime(meta.generated_at, uiLocale)}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-c4 text-xs">Перевод:</span>
          <Badge variant="default">{locale.translation_status}</Badge>
        </div>
      </div>

      {applied_persona && (
        <div
          className="flex flex-col gap-2"
          data-testid="decision-persona-meta"
        >
          <div className="flex items-center gap-2">
            <span className="text-c4 text-xs">
              Рейтинг адаптирован под профиль:
            </span>
            <strong className="text-c1 text-sm">{applied_persona.name}</strong>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-c4 text-xs">Режим ранжирования:</span>
            <Badge variant="default">{ranking_mode}</Badge>
          </div>
        </div>
      )}

      <DecisionPersonalizationSummary personalization={personalization} />

      {winner && (
        <div data-testid="decision-winner-block">
          <Card
            accent="gold"
            interactive={false}
            className="flex flex-col gap-2"
          >
            <Kicker>Рекомендуемый вариант</Kicker>
            <div className="flex items-baseline justify-between gap-3">
              <span className="font-display text-2xl font-bold">
                {winner.country.name}
              </span>
              <div className="flex items-center gap-2">
                <span className="font-display text-gold3 text-2xl font-bold">
                  {formatScore(winner.persona_adjusted_score ?? winner.score)}
                </span>
                <AIExplainNumberButton
                  numberType="decision_score"
                  countrySlug={winner.country.slug}
                  scenarioSlug={scenario.slug}
                  value={winner.persona_adjusted_score ?? winner.score}
                  locale={asSupportedLocale(locale.resolved_locale)}
                />
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              <Badge variant="default">{winner.score_label}</Badge>
              {winner.confidence && (
                <ConfidenceBadge confidence={winner.confidence} />
              )}
            </div>
            {winner.summary && (
              <p className="text-c3 text-sm leading-relaxed">
                {winner.summary}
              </p>
            )}
          </Card>
        </div>
      )}

      {results.length === 0 ? (
        <EmptyState message="Результаты подбора не получены." />
      ) : (
        <div className="flex flex-col gap-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h3 className="font-display text-lg font-semibold">
              Полный рейтинг
            </h3>
            {results.length >= 2 && (
              <Link
                href={`/compare?countries=${results
                  .slice(0, 3)
                  .map((r) => r.country.slug)
                  .join(",")}`}
                className="text-gold3 hover:text-gold text-sm transition-colors duration-300"
                data-testid="compare-top-results-link"
              >
                Сравнить топ-{Math.min(3, results.length)} бок-о-бок{" "}
                <ArrowNext />
              </Link>
            )}
          </div>
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
