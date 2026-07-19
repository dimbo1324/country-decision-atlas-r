import { useTranslations } from "next-intl";
import { EmptyState } from "../../shared/ui/EmptyState";

export function TimelineEmptyState() {
  const t = useTranslations("legalSignalsTimeline");
  return (
    <div data-testid="legal-signals-timeline-empty">
      <EmptyState message={t("noEventsForFilters")} />
    </div>
  );
}
