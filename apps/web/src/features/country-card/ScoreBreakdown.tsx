import type { CountryReadModelResponse } from "../../shared/api/countries";

type ScoreBreakdownItem = NonNullable<
  CountryReadModelResponse["scores"][number]["breakdowns"]
>[number];

type ScoreBreakdownProps = {
  breakdowns: ScoreBreakdownItem[];
};

export function ScoreBreakdown({ breakdowns }: ScoreBreakdownProps) {
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
          {breakdowns.map((b, i) => (
            <tr key={i}>
              <td>{b.criterion}</td>
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
