import type { DecisionRunResponse } from "../../shared/api/decision";

type DecisionBreakdownItem =
  DecisionRunResponse["results"][number]["breakdown"][number];

type DecisionBreakdownProps = {
  breakdown: DecisionBreakdownItem[];
};

export function DecisionBreakdown({ breakdown }: DecisionBreakdownProps) {
  if (breakdown.length === 0) return null;

  return (
    <div className="breakdownWrap">
      <table className="breakdownTable">
        <thead>
          <tr>
            <th>Критерий</th>
            <th>Оценка</th>
            <th>Вес</th>
            <th>Взвешенная</th>
            <th>Достоверность</th>
          </tr>
        </thead>
        <tbody>
          {breakdown.map((b) => (
            <tr key={b.criterion}>
              <td>{b.title || b.criterion}</td>
              <td>{b.score}</td>
              <td>{b.weight}</td>
              <td>{b.weighted_score}</td>
              <td>{b.confidence ?? "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
