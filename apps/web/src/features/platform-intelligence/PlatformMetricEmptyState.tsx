import { EmptyState } from "../../shared/ui/EmptyState";

export function PlatformMetricEmptyState() {
  return (
    <div data-testid="platform-intelligence-empty">
      <EmptyState message="Метрики платформенного интеллекта ещё не вычислены для этой страны." />
    </div>
  );
}
