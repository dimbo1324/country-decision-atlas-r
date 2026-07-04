export function RouteEmptyState({ message }: { message?: string }) {
  return (
    <div
      className="emptyNotice"
      data-testid="routes-empty"
    >
      {message ?? "Для выбранных условий маршруты пока отсутствуют."}
    </div>
  );
}
