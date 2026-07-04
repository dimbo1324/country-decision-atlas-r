type Props = {
  message?: string;
};

export function MatrixEmptyState({ message }: Props) {
  return (
    <div
      className="matrixEmptyState"
      data-testid="compare-matrix-empty"
    >
      <p>{message ?? "Нет данных для матрицы."}</p>
    </div>
  );
}
