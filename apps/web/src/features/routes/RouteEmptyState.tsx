import { EmptyState } from "../../shared/ui/EmptyState";

export function RouteEmptyState({ message }: { message?: string }) {
  return (
    <div data-testid="routes-empty">
      <EmptyState
        message={message ?? "Для выбранных условий маршруты пока отсутствуют."}
      />
    </div>
  );
}
