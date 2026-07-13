import { EmptyState } from "../../shared/ui/EmptyState";

export function DataJournalEmptyState() {
  return (
    <div data-testid="data-journal-empty">
      <EmptyState message="Пока нет опубликованных обновлений данных для этой страны." />
    </div>
  );
}
