import { Badge, SignalTicker, cn } from "@country-decision-atlas/ui";
import { Link } from "../../i18n/navigation";
import type { LatestLegalEvent } from "../../shared/api/home";
import { ArrowNext } from "../../shared/ui/LinkArrow";

const DIRECTION_LABELS: Record<string, string> = {
  positive: "Положительное",
  negative: "Негативное",
  neutral: "Нейтральное",
  mixed: "Смешанное",
  uncertain: "Неопределённое",
};

const DIRECTION_TEXT_CLASS: Record<string, string> = {
  positive: "text-sage3",
  negative: "text-terra3",
};

function formatDate(value: string): string {
  return new Date(`${value}T00:00:00`).toLocaleDateString("ru-RU", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function LatestLegalEventsPanel({
  events,
}: {
  events: LatestLegalEvent[];
}) {
  const tickerItems = events.map(
    (event) => `${event.country_name} · ${event.title}`,
  );

  return (
    <section aria-labelledby="home-events-title">
      <div className="mb-5 flex items-end justify-between gap-4">
        <h2
          id="home-events-title"
          className="font-display text-2xl font-semibold"
        >
          Последние правовые изменения
        </h2>
        <Link
          href="/legal-signals"
          className="font-mono text-c3 hover:text-gold3 text-[10px] tracking-[0.2em] uppercase transition-colors duration-300"
        >
          Открыть правовые сигналы <ArrowNext />
        </Link>
      </div>
      <div data-testid="home-latest-legal-events">
        {events.length === 0 ? (
          <p className="text-c3 text-sm">Недавние события пока недоступны.</p>
        ) : (
          <>
            {tickerItems.length > 0 && (
              <div className="mb-4">
                <SignalTicker items={tickerItems} />
              </div>
            )}
            <ul className="flex flex-col">
              {events.map((event) => (
                <li
                  key={`${event.country_slug}:${event.event_date}:${event.title}`}
                  className="border-warm flex flex-col gap-1.5 border-b py-3.5 last:border-b-0"
                >
                  <div className="flex flex-wrap items-center gap-2">
                    <time
                      dateTime={event.event_date}
                      className="font-mono text-c4 text-[9px] tracking-[0.12em]"
                    >
                      {formatDate(event.event_date)}
                    </time>
                    <span className="text-c3 text-xs">
                      {event.country_name}
                    </span>
                    <Badge
                      variant={
                        event.impact_direction === "positive"
                          ? "positive"
                          : event.impact_direction === "negative"
                            ? "negative"
                            : "default"
                      }
                    >
                      {DIRECTION_LABELS[event.impact_direction] ??
                        event.impact_direction}
                    </Badge>
                    <span className="font-mono text-c4 text-[9px] tracking-[0.12em] uppercase">
                      {event.impact_level}
                    </span>
                  </div>
                  <strong
                    className={cn(
                      "font-display text-sm font-semibold",
                      DIRECTION_TEXT_CLASS[event.impact_direction] ?? "text-c1",
                    )}
                  >
                    {event.title}
                  </strong>
                  {event.summary && (
                    <p className="text-c3 text-xs leading-relaxed">
                      {event.summary}
                    </p>
                  )}
                  {event.source && (
                    <a
                      href={event.source.url}
                      target="_blank"
                      rel="noreferrer"
                      className="font-mono text-c4 hover:text-gold3 text-[9px] tracking-[0.1em] uppercase transition-colors duration-300"
                    >
                      Источник: {event.source.title}
                    </a>
                  )}
                </li>
              ))}
            </ul>
          </>
        )}
      </div>
    </section>
  );
}
