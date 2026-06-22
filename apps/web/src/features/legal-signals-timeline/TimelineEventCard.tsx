import Link from "next/link";
import type { LocaleCode } from "../../shared/api/countries";
import type { LegalSignalTimelineEvent } from "../../shared/api/legal-signals";
import { routes } from "../../shared/lib/routes";
import { LocalizationBadge } from "../../shared/ui/LocalizationBadge";

const directionLabels: Record<string, string> = {
  positive: "Положительное",
  negative: "Негативное",
  neutral: "Нейтральное",
  mixed: "Смешанное",
  uncertain: "Неопределённое",
};
const levelLabels: Record<string, string> = {
  low: "Низкий",
  medium: "Средний",
  high: "Высокий",
  critical: "Критический",
};
const typeLabels: Record<string, string> = {
  law: "Закон",
  bill: "Законопроект",
  policy: "Политика",
  court_decision: "Судебное решение",
  administrative_change: "Административное изменение",
  political_signal: "Политический сигнал",
  other: "Другое",
};

export function TimelineEventCard({
  event,
  locale,
}: {
  event: LegalSignalTimelineEvent;
  locale: LocaleCode;
}) {
  const directionClass = `timelineEvent${capitalize(event.impact_direction)}`;
  return (
    <article
      className={`timelineEventCard ${directionClass}`}
      data-testid="timeline-event-card"
    >
      <div className="timelineEventMarker" aria-hidden="true" />
      <div className="timelineEventMeta">
        <time dateTime={event.event_date}>
          {formatEventDate(event.event_date, locale)}
        </time>
        <span>{event.country_name}</span>
        <span>{typeLabels[event.signal_type] ?? event.signal_type}</span>
        <span>{directionLabels[event.impact_direction]}</span>
        <span>Уровень: {levelLabels[event.impact_level] ?? event.impact_level}</span>
      </div>
      <h3>{event.title}</h3>
      {event.summary && <p>{event.summary}</p>}
      {(event.affected_groups ?? []).length > 0 && (
        <div className="timelineAffectedGroups">
          <strong>Затронутые группы:</strong> {(event.affected_groups ?? []).join(", ")}
        </div>
      )}
      <div className="timelineEventEvidence">
        {event.source && (
          <a
            href={event.source.url}
            target="_blank"
            rel="noreferrer"
            className="externalLink"
          >
            Источник: {event.source.title}
          </a>
        )}
        {event.evidence?.url && (
          <a
            href={event.evidence.url}
            target="_blank"
            rel="noreferrer"
            className="externalLink"
          >
            Доказательство: {event.evidence.claim}
          </a>
        )}
        {!event.evidence?.url && event.evidence && (
          <span>Доказательство: {event.evidence.claim}</span>
        )}
        <Link
          href={routes.countryWithLocale(event.country_slug, locale)}
          className="internalLink"
        >
          Карточка страны: {event.country_name} →
        </Link>
        <Link href={`/sources?country_slug=${event.country_slug}&locale=${locale}`}>
          Все источники страны
        </Link>
      </div>
      {event.localization && <LocalizationBadge localization={event.localization} />}
    </article>
  );
}

function capitalize(value: string) {
  return `${value.charAt(0).toUpperCase()}${value.slice(1)}`;
}

function formatEventDate(value: string, locale: LocaleCode) {
  return new Date(`${value}T00:00:00`).toLocaleDateString(
    locale === "ru" ? "ru-RU" : "en-US",
    { year: "numeric", month: "long", day: "numeric" },
  );
}
