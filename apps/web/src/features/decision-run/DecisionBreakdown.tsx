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
            <th>Criterion</th>
            <th>Score</th>
            <th>Weight</th>
            <th>Weighted</th>
            <th>Confidence</th>
          </tr>
        </thead>
        <tbody>
          {breakdown.map((b, i) => (
            <tr key={i}>
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
