import type { TimelineYearGroup as TimelineYearGroupData } from "../../shared/api/legal-signals";
import type { SupportedLocale } from "../../shared/lib/locale";
import { TimelineEventCard } from "./TimelineEventCard";

export function TimelineYearGroup({
  group,
  locale,
  onShowEvidence,
}: {
  group: TimelineYearGroupData;
  locale: SupportedLocale;
  onShowEvidence: (signalId: string, title: string) => void;
}) {
  return (
    <section
      className="flex flex-col gap-4"
      data-testid={`timeline-year-${group.year}`}
    >
      <h2
        className="font-display text-c1 text-2xl font-semibold"
        data-testid="timeline-year-heading"
      >
        {group.year}
      </h2>
      <div className="flex flex-col gap-3">
        {group.events.map((event) => (
          <TimelineEventCard
            key={event.id}
            event={event}
            locale={locale}
            onShowEvidence={onShowEvidence}
          />
        ))}
      </div>
    </section>
  );
}
