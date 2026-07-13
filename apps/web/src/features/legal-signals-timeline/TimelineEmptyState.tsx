import { EmptyState } from "../../shared/ui/EmptyState";

export function TimelineEmptyState() {
  return (
    <div data-testid="legal-signals-timeline-empty">
      <EmptyState message="По выбранным фильтрам событий не найдено." />
    </div>
  );
}
