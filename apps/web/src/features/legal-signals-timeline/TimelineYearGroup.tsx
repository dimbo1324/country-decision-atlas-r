import type { LocaleCode } from "../../shared/api/countries";
import type { TimelineYearGroup as TimelineYearGroupData } from "../../shared/api/legal-signals";
import { TimelineEventCard } from "./TimelineEventCard";

export function TimelineYearGroup({
  group,
  locale,
}: {
  group: TimelineYearGroupData;
  locale: LocaleCode;
}) {
  return (
    <section
      className="timelineYearGroup"
      data-testid={`timeline-year-${group.year}`}
    >
      <h2 className="timelineYearTitle">{group.year}</h2>
      <div className="timelineYearEvents">
        {group.events.map((event) => (
          <TimelineEventCard
            key={event.id}
            event={event}
            locale={locale}
          />
        ))}
      </div>
    </section>
  );
}
