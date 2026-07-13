type DecisionWeightSummaryProps = {
  sum: number;
};

export function DecisionWeightSummary({ sum }: DecisionWeightSummaryProps) {
  return (
    <div className="flex flex-col gap-1">
      <span className="text-c3 text-sm">Сумма приоритетов: {sum}</span>
      {sum === 0 && (
        <p
          role="alert"
          className="text-terra3 text-sm"
        >
          Сумма приоритетов должна быть больше нуля.
        </p>
      )}
    </div>
  );
}
