import { useTranslations } from "next-intl";
import { Badge, Card } from "@country-decision-atlas/ui";
import { Link } from "../../i18n/navigation";
import type { LegalSignalTimelineEvent } from "../../shared/api/legal-signals";
import { DATE_FORMAT_LOCALE } from "../../shared/lib/format";
import type { SupportedLocale } from "../../shared/lib/locale";
import { routes } from "../../shared/lib/routes";
import { LocalizationBadge } from "../../shared/ui/LocalizationBadge";
import { ArrowNext } from "../../shared/ui/LinkArrow";
import {
  ImpactDirectionBadge,
  ImpactLevelBadge,
} from "../../shared/ui/ImpactBadge";

const TYPE_LABELS: Record<SupportedLocale, Record<string, string>> = {
  en: {
    law: "Law",
    bill: "Bill",
    policy: "Policy",
    court_decision: "Court decision",
    administrative_change: "Administrative change",
    political_signal: "Political signal",
    other: "Other",
  },
  ru: {
    law: "Закон",
    bill: "Законопроект",
    policy: "Политика",
    court_decision: "Судебное решение",
    administrative_change: "Административное изменение",
    political_signal: "Политический сигнал",
    other: "Другое",
  },
  es: {
    law: "Ley",
    bill: "Proyecto de ley",
    policy: "Política",
    court_decision: "Decisión judicial",
    administrative_change: "Cambio administrativo",
    political_signal: "Señal política",
    other: "Otro",
  },
};

export function TimelineEventCard({
  event,
  locale,
  onShowEvidence,
}: {
  event: LegalSignalTimelineEvent;
  /** The real interface locale, not the backend's en/ru-only `LocaleCode`
   * -- this component only uses it for date/label display, never for a
   * data fetch, so it can safely carry `es` through. */
  locale: SupportedLocale;
  onShowEvidence: (signalId: string, title: string) => void;
}) {
  const t = useTranslations("timelineEventCard");
  return (
    <div data-testid="legal-signal-event-card">
      <Card
        interactive={false}
        className="flex flex-col gap-3"
      >
        <div className="flex flex-wrap items-center justify-between gap-2">
          <span className="font-display text-base font-semibold">
            {event.title}
          </span>
          <div className="flex items-center gap-2">
            <Badge variant="default">
              {TYPE_LABELS[locale][event.signal_type] ?? event.signal_type}
            </Badge>
            {event.localization && (
              <LocalizationBadge
                localization={event.localization}
                compact
              />
            )}
          </div>
        </div>
        <div className="font-mono text-c3 flex flex-wrap items-center gap-3 text-[10px] tracking-[0.1em] uppercase">
          <time dateTime={event.event_date}>
            {formatEventDate(event.event_date, locale)}
          </time>
          <span>{event.country_name}</span>
        </div>
        {event.summary && (
          <p className="text-c3 text-sm leading-relaxed">{event.summary}</p>
        )}
        <div className="flex flex-wrap gap-2">
          <ImpactDirectionBadge direction={event.impact_direction} />
          <ImpactLevelBadge level={event.impact_level} />
        </div>
        {(event.affected_groups ?? []).length > 0 && (
          <p className="text-c4 text-xs">
            <strong className="text-c3">{t("affectedGroups")}</strong>{" "}
            {(event.affected_groups ?? []).join(", ")}
          </p>
        )}
        <div className="flex flex-wrap items-center gap-4 text-sm">
          {event.source && (
            <a
              href={event.source.url}
              target="_blank"
              rel="noreferrer"
              data-testid="legal-signal-source-link"
              className="text-gold3 hover:text-gold transition-colors duration-300"
            >
              {t("source", { title: event.source.title })}
            </a>
          )}
          <Link
            href={routes.country(event.country_slug)}
            className="text-c3 hover:text-c1 transition-colors duration-300"
          >
            {t("countryCard", { name: event.country_name })} <ArrowNext />
          </Link>
          <Link
            href={routes.sourcesForCountry(event.country_slug)}
            className="text-c3 hover:text-c1 transition-colors duration-300"
          >
            {t("allCountrySources")}
          </Link>
          <button
            type="button"
            onClick={() => onShowEvidence(event.legal_signal_id, event.title)}
            data-testid="legal-signal-evidence-toggle"
            className="font-mono text-c3 hover:text-gold3 text-[10px] tracking-[0.15em] uppercase transition-colors duration-300"
          >
            {t("evidence")} <ArrowNext />
          </button>
        </div>
      </Card>
    </div>
  );
}

function formatEventDate(value: string, locale: SupportedLocale) {
  return new Date(`${value}T00:00:00`).toLocaleDateString(
    DATE_FORMAT_LOCALE[locale],
    { year: "numeric", month: "long", day: "numeric" },
  );
}
