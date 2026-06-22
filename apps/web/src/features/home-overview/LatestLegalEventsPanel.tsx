import Link from "next/link";
import type { LatestLegalEvent } from "../../shared/api/home";

const directionLabels: Record<string, string> = {
  positive: "Положительное",
  negative: "Негативное",
  neutral: "Нейтральное",
  mixed: "Смешанное",
  uncertain: "Неопределённое",
};

export function LatestLegalEventsPanel({ events }: { events: LatestLegalEvent[] }) {
  return (
    <section className="homeOverviewSection" aria-labelledby="home-events-title">
      <div className="homeSectionHeading">
        <h2 id="home-events-title">Последние правовые изменения</h2>
        <Link href="/legal-signals">Открыть правовые сигналы</Link>
      </div>
      <div className="homeLegalEvents" data-testid="home-latest-legal-events">
        {events.length === 0 ? (
          <span>Недавние события пока недоступны.</span>
        ) : (
          events.map((event) => (
            <article
              className={`homeLegalEvent homeEvent${capitalize(event.impact_direction)}`}
              key={`${event.country_slug}:${event.event_date}:${event.title}`}
            >
              <div className="homeLegalEventMeta">
                <time dateTime={event.event_date}>{formatDate(event.event_date)}</time>
                <span>{event.country_name}</span>
                <span>
                  {directionLabels[event.impact_direction] ?? event.impact_direction}
                </span>
                <span>{event.impact_level}</span>
              </div>
              <h3>{event.title}</h3>
              {event.summary && <p>{event.summary}</p>}
              {event.source && (
                <a href={event.source.url} target="_blank" rel="noreferrer">
                  Источник: {event.source.title}
                </a>
              )}
            </article>
          ))
        )}
      </div>
    </section>
  );
}

function capitalize(value: string) {
  return `${value.charAt(0).toUpperCase()}${value.slice(1)}`;
}

function formatDate(value: string) {
  return new Date(`${value}T00:00:00`).toLocaleDateString("ru-RU", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}
