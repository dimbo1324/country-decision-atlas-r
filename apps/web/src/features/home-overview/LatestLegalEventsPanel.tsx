import { useTranslations } from "next-intl";
import { Badge, SignalTicker, cn } from "@country-decision-atlas/ui";
import { Link } from "../../i18n/navigation";
import type { LatestLegalEvent } from "../../shared/api/home";
import { DATE_FORMAT_LOCALE } from "../../shared/lib/format";
import type { SupportedLocale } from "../../shared/lib/locale";
import { useAppLocale } from "../../shared/lib/useAppLocale";
import { ArrowNext } from "../../shared/ui/LinkArrow";

const DIRECTION_KEY: Record<string, string> = {
  positive: "directionPositive",
  negative: "directionNegative",
  neutral: "directionNeutral",
  mixed: "directionMixed",
  uncertain: "directionUncertain",
};

const DIRECTION_TEXT_CLASS: Record<string, string> = {
  positive: "text-sage3",
  negative: "text-terra3",
};

/** Appends a local-midnight time (not the shared `formatDate`, which parses
 * the bare date as UTC midnight) so a date-only string like "2026-01-15"
 * can't roll back a day in timezones behind UTC. */
function formatEventDate(value: string, locale: SupportedLocale): string {
  return new Date(`${value}T00:00:00`).toLocaleDateString(
    DATE_FORMAT_LOCALE[locale],
    { year: "numeric", month: "short", day: "numeric" },
  );
}

export function LatestLegalEventsPanel({
  events,
}: {
  events: LatestLegalEvent[];
}) {
  const t = useTranslations("home");
  const locale = useAppLocale();
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
          {t("legalEventsTitle")}
        </h2>
        <Link
          href="/legal-signals"
          className="font-mono text-c3 hover:text-gold3 text-[10px] tracking-[0.2em] uppercase transition-colors duration-300"
        >
          {t("openLegalSignals")} <ArrowNext />
        </Link>
      </div>
      <div data-testid="home-latest-legal-events">
        {events.length === 0 ? (
          <p className="text-c3 text-sm">{t("legalEventsEmpty")}</p>
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
                      {formatEventDate(event.event_date, locale)}
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
                      {DIRECTION_KEY[event.impact_direction]
                        ? t(DIRECTION_KEY[event.impact_direction])
                        : event.impact_direction}
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
                      {t("sourceLabel", { title: event.source.title })}
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
