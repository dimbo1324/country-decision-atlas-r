type DecisionWeightSummaryProps = {
  sum: number;
};

export function DecisionWeightSummary({ sum }: DecisionWeightSummaryProps) {
  return (
    <div className="decisionWeightSummary">
      <span>Сумма приоритетов: {sum}</span>
      {sum === 0 && (
        <p className="decisionWeightWarning" role="alert">
          Сумма приоритетов должна быть больше нуля.
        </p>
      )}
    </div>
  );
}
