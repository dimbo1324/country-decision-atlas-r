import { useTranslations } from "next-intl";
import {
  Accordion,
  Badge,
  Card,
  type AccordionItem,
} from "@country-decision-atlas/ui";
import { Link } from "../../i18n/navigation";
import type { DecisionRunResponse } from "../../shared/api/decision";
import type { SupportedLocale } from "../../shared/lib/locale";
import { routes } from "../../shared/lib/routes";
import { useAppLocale } from "../../shared/lib/useAppLocale";
import { ConfidenceBadge } from "../../shared/ui/ConfidenceBadge";
import { LocalizationBadge } from "../../shared/ui/LocalizationBadge";
import { formatScore } from "../../shared/lib/format";
import { DecisionBreakdown } from "./DecisionBreakdown";
import { DecisionCountryTrustBadge } from "./DecisionCountryTrustBadge";
import { DecisionSources } from "./DecisionSources";
import { DecisionWarnings } from "./DecisionWarnings";
import { ArrowNext } from "../../shared/ui/LinkArrow";

type DecisionCountryResult = DecisionRunResponse["results"][number];
type OriginContextStatus = DecisionRunResponse["origin_context_status"];

type DecisionResultCardProps = {
  result: DecisionCountryResult;
  locale: SupportedLocale;
  originContextStatus?: OriginContextStatus;
};

const COMPATIBILITY_LABELS: Record<SupportedLocale, Record<string, string>> = {
  en: {
    favourable: "Favourable",
    mixed: "Mixed",
    restrictive: "Restrictive",
    unknown: "Unknown",
  },
  ru: {
    favourable: "Благоприятно",
    mixed: "Смешанно",
    restrictive: "Ограничено",
    unknown: "Неизвестно",
  },
  es: {
    favourable: "Favorable",
    mixed: "Mixto",
    restrictive: "Restrictivo",
    unknown: "Desconocido",
  },
};

const FRESHNESS_LABELS: Record<SupportedLocale, Record<string, string>> = {
  en: {
    fresh: "fresh",
    current: "current",
    stale: "stale",
    unknown: "unknown",
  },
  ru: {
    fresh: "свежие",
    current: "актуальные",
    stale: "устаревшие",
    unknown: "неизвестно",
  },
  es: {
    fresh: "actualizados",
    current: "vigentes",
    stale: "desactualizados",
    unknown: "desconocido",
  },
};

const NOTE_TYPE_LABELS: Record<SupportedLocale, Record<string, string>> = {
  en: {
    visa: "Visa",
    banking: "Banking",
    tax: "Taxes",
    flight_logistics: "Flight logistics",
    timezone: "Time zone",
    language: "Language",
    migration_restriction: "Migration restrictions",
  },
  ru: {
    visa: "Виза",
    banking: "Банки",
    tax: "Налоги",
    flight_logistics: "Логистика перелётов",
    timezone: "Часовой пояс",
    language: "Язык",
    migration_restriction: "Миграционные ограничения",
  },
  es: {
    visa: "Visado",
    banking: "Banca",
    tax: "Impuestos",
    flight_logistics: "Logística de vuelos",
    timezone: "Zona horaria",
    language: "Idioma",
    migration_restriction: "Restricciones migratorias",
  },
};

function OriginAwareContext({
  result,
  originContextStatus,
}: {
  result: DecisionCountryResult;
  originContextStatus?: OriginContextStatus;
}) {
  const t = useTranslations("decisionRun");
  const locale = useAppLocale();
  return (
    <div data-testid="origin-aware-context">
      {!originContextStatus || originContextStatus === "not_requested" ? (
        <p
          className="text-c4 text-sm"
          data-testid="origin-context-not-requested"
        >
          {t("specifyOrigin")}
        </p>
      ) : result.country_pair_context ? (
        <div
          className="flex flex-col gap-2"
          data-testid="origin-pair-context"
        >
          <div className="flex flex-wrap gap-2">
            <Badge variant="default">
              {COMPATIBILITY_LABELS[locale][
                result.country_pair_context.compatibility_label
              ] ?? result.country_pair_context.compatibility_label}
            </Badge>
            <ConfidenceBadge
              confidence={result.country_pair_context.confidence}
            />
            <Badge variant="default">
              {t("dataLabel", {
                value:
                  FRESHNESS_LABELS[locale][
                    result.country_pair_context.freshness_status
                  ] ?? result.country_pair_context.freshness_status,
              })}
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
                    {NOTE_TYPE_LABELS[locale][note.type] ?? note.type}:
                  </strong>{" "}
                  {note.message}
                </li>
              ))}
            </ul>
          )}
          {(result.country_pair_context.source_ids ?? []).length > 0 && (
            <p className="text-c4 text-xs">
              {t("sourcesCount", {
                count: (result.country_pair_context.source_ids ?? []).length,
              })}
            </p>
          )}
        </div>
      ) : (
        <p
          className="text-c4 text-sm"
          data-testid="origin-pair-context-empty"
        >
          {t("noRouteDataYet")}
        </p>
      )}
    </div>
  );
}

export function DecisionResultCard({
  result,
  locale,
  originContextStatus,
}: DecisionResultCardProps) {
  const t = useTranslations("decisionRun");
  const [topStrength, ...restStrengths] = result.strengths;

  // Route context is deliberately accordion item 0 -- Accordion opens
  // its first item by default, so this stays visible with zero clicks,
  // matching web-mvp-origin-aware-decision.spec.ts's existing assertion
  // that origin-aware-context/origin-context-not-requested render without
  // any interaction.
  const accordionItems: AccordionItem[] = [
    {
      title: t("routeContext"),
      content: (
        <OriginAwareContext
          result={result}
          originContextStatus={originContextStatus}
        />
      ),
    },
  ];

  if (restStrengths.length > 0) {
    accordionItems.push({
      title: t("otherStrengths"),
      content: (
        <ul className="flex flex-col gap-1">
          {restStrengths.map((s) => (
            <li key={s.message}>{s.message}</li>
          ))}
        </ul>
      ),
    });
  }

  if (result.weaknesses.length > 0) {
    accordionItems.push({
      title: t("weaknesses"),
      content: (
        <ul className="flex flex-col gap-1">
          {result.weaknesses.map((w) => (
            <li key={w.message}>{w.message}</li>
          ))}
        </ul>
      ),
    });
  }

  if (result.risk_warnings.length > 0) {
    accordionItems.push({
      title: t("risks"),
      meta: String(result.risk_warnings.length),
      content: <DecisionWarnings warnings={result.risk_warnings} />,
    });
  }

  if (result.breakdown.length > 0) {
    accordionItems.push({
      title: t("scoreBreakdown"),
      content: <DecisionBreakdown breakdown={result.breakdown} />,
    });
  }

  accordionItems.push({
    title: t("sources"),
    content: <DecisionSources sources={result.sources} />,
  });

  return (
    <div data-testid="result-card">
      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <div className="flex flex-wrap items-center gap-2">
          <span
            className="font-display text-gold3 text-xl font-bold"
            aria-label={t("rank", { rank: result.rank })}
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
          {result.confidence && (
            <ConfidenceBadge confidence={result.confidence} />
          )}
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
            <span className="text-c3">
              {t("baseScore", { value: formatScore(result.score) })}
            </span>
            <span className="text-c2 font-semibold">
              {t("personaAdjustedScore", {
                value: formatScore(result.persona_adjusted_score),
              })}
            </span>
          </div>
        )}

        {topStrength && (
          <p className="text-sm">
            <span className="font-mono text-sage3 text-[9px] tracking-[0.2em] uppercase">
              {t("strengthLabel")}{" "}
            </span>
            <span className="text-c2">{topStrength.message}</span>
          </p>
        )}

        <Accordion items={accordionItems} />

        <Link
          href={routes.country(result.country.slug)}
          className="text-gold3 hover:text-gold text-sm transition-colors duration-300"
        >
          {t("countryCard")} <ArrowNext />
        </Link>
      </Card>
    </div>
  );
}
