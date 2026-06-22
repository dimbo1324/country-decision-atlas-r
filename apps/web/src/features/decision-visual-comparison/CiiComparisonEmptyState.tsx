type Props = {
  message?: string;
};

export function CiiComparisonEmptyState({ message }: Props) {
  return (
    <div className="ciiCompareEmpty">
      <p className="ciiCompareEmptyText">
        {message ?? "Визуальное сравнение CII недоступно"}
      </p>
    </div>
  );
}
