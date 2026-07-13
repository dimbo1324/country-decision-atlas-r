import { Badge, Card } from "@country-decision-atlas/ui";
import { Link } from "../../i18n/navigation";
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

const FRESHNESS_LABELS: Record<string, string> = {
  fresh: "свежие",
  current: "актуальные",
  stale: "устаревшие",
  unknown: "неизвестно",
};

const NOTE_TYPE_LABELS: Record<string, string> = {
  visa: "Виза",
  banking: "Банки",
  tax: "Налоги",
  flight_logistics: "Логистика перелётов",
  timezone: "Часовой пояс",
  language: "Язык",
  migration_restriction: "Миграционные ограничения",
};

export function DecisionResultCard({
  result,
  locale,
  originContextStatus,
}: DecisionResultCardProps) {
  return (
    <div data-testid="result-card">
    <Card
      interactive={false}
      className="flex flex-col gap-4"
    >
      <div className="flex flex-wrap items-center gap-2">
        <span
          className="font-display text-gold3 text-xl font-bold"
          aria-label={`Место ${result.rank}`}
        >
          #{result.rank}
        </span>
        <span className="font-display text-lg font-semibold">
          {result.country.name}
        </span>
        <span className="font-display text-c1 ml-auto text-xl font-bold">
          {formatScore(result.score)}
        </span>
        <Badge variant="default">{result.score_label}</Badge>
        {result.confidence && <ConfidenceBadge confidence={result.confidence} />}
        <LocalizationBadge
          localization={result.localization}
          compact
        />
      </div>

      <DecisionCountryTrustBadge
        countrySlug={result.country.slug}
        locale={locale}
      />

      {result.summary && (
        <p className="text-c3 text-sm leading-relaxed">{result.summary}</p>
      )}

      {result.persona_adjusted_score != null && (
        <div
          className="flex flex-wrap gap-4 text-sm"
          data-testid="persona-adjusted-score"
        >
          <span className="text-c3">Базовая оценка: {formatScore(result.score)}</span>
          <span className="text-c2 font-semibold">
            Оценка с учетом персоны:{" "}
            {formatScore(result.persona_adjusted_score)}
          </span>
        </div>
      )}

      {result.strengths.length > 0 && (
        <div className="flex flex-col gap-2">
          <h4 className="font-mono text-sage3 text-[9px] tracking-[0.2em] uppercase">
            Сильные стороны
          </h4>
          <ul className="text-c3 flex flex-col gap-1 text-sm">
            {result.strengths.map((s) => (
              <li key={s.message}>{s.message}</li>
            ))}
          </ul>
        </div>
      )}

      {result.weaknesses.length > 0 && (
        <div className="flex flex-col gap-2">
          <h4 className="font-mono text-terra3 text-[9px] tracking-[0.2em] uppercase">
            Слабые стороны
          </h4>
          <ul className="text-c3 flex flex-col gap-1 text-sm">
            {result.weaknesses.map((w) => (
              <li key={w.message}>{w.message}</li>
            ))}
          </ul>
        </div>
      )}

      {result.risk_warnings.length > 0 && (
        <div className="flex flex-col gap-2">
          <h4 className="font-mono text-terra3 text-[9px] tracking-[0.2em] uppercase">
            Риски
          </h4>
          <DecisionWarnings warnings={result.risk_warnings} />
        </div>
      )}

      <div
        className="flex flex-col gap-2"
        data-testid="origin-aware-context"
      >
        <h4 className="font-mono text-c4 text-[9px] tracking-[0.2em] uppercase">
          Контекст маршрута
        </h4>
        {!originContextStatus || originContextStatus === "not_requested" ? (
          <p
            className="text-c4 text-sm"
            data-testid="origin-context-not-requested"
          >
            Укажите страну отправления, чтобы увидеть контекст маршрута.
          </p>
        ) : result.country_pair_context ? (
          <div
            className="flex flex-col gap-2"
            data-testid="origin-pair-context"
          >
            <div className="flex flex-wrap gap-2">
              <Badge variant="default">
                {COMPATIBILITY_LABELS[
                  result.country_pair_context.compatibility_label
                ] ?? result.country_pair_context.compatibility_label}
              </Badge>
              <ConfidenceBadge
                confidence={result.country_pair_context.confidence}
              />
              <Badge variant="default">
                Данные:{" "}
                {FRESHNESS_LABELS[
                  result.country_pair_context.freshness_status
                ] ?? result.country_pair_context.freshness_status}
              </Badge>
            </div>
            {result.country_pair_context.practical_summary && (
              <p className="text-c3 text-sm">
                {result.country_pair_context.practical_summary}
              </p>
            )}
            {(result.country_pair_context.key_notes ?? []).length > 0 && (
              <ul className="text-c3 flex flex-col gap-1 text-sm">
                {(result.country_pair_context.key_notes ?? []).map((note) => (
                  <li key={note.type}>
                    <strong className="text-c2">
                      {NOTE_TYPE_LABELS[note.type] ?? note.type}:
                    </strong>{" "}
                    {note.message}
                  </li>
                ))}
              </ul>
            )}
            {(result.country_pair_context.source_ids ?? []).length > 0 && (
              <p className="text-c4 text-xs">
                Источников:{" "}
                {(result.country_pair_context.source_ids ?? []).length}
              </p>
            )}
          </div>
        ) : (
          <p
            className="text-c4 text-sm"
            data-testid="origin-pair-context-empty"
          >
            Пока нет данных по этому маршруту.
          </p>
        )}
      </div>

      {result.breakdown.length > 0 && (
        <div className="flex flex-col gap-2">
          <h4 className="font-mono text-c4 text-[9px] tracking-[0.2em] uppercase">
            Разбор оценки
          </h4>
          <DecisionBreakdown breakdown={result.breakdown} />
        </div>
      )}

      <div className="flex flex-col gap-2">
        <h4 className="font-mono text-c4 text-[9px] tracking-[0.2em] uppercase">
          Источники
        </h4>
        <DecisionSources sources={result.sources} />
      </div>

      <Link
        href={routes.country(result.country.slug)}
        className="text-gold3 hover:text-gold text-sm transition-colors duration-300"
      >
        Карточка страны →
      </Link>
    </Card>
    </div>
  );
}
