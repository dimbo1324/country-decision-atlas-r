import { EmptyState } from "../../shared/ui/EmptyState";

type Props = {
  message?: string;
};

export function MatrixEmptyState({ message }: Props) {
  return (
    <div data-testid="compare-matrix-empty">
      <EmptyState message={message ?? "Нет данных для матрицы."} />
    </div>
  );
}
