import { DataTable } from "@country-decision-atlas/ui";
import type { DecisionRunResponse } from "../../shared/api/decision";

type DecisionBreakdownItem =
  DecisionRunResponse["results"][number]["breakdown"][number];

type DecisionBreakdownProps = {
  breakdown: DecisionBreakdownItem[];
};

export function DecisionBreakdown({ breakdown }: DecisionBreakdownProps) {
  if (breakdown.length === 0) return null;

  return (
    <DataTable
      columns={[
        { header: "Критерий" },
        { header: "Оценка", numeric: true, align: "right" },
        { header: "Вес", numeric: true, align: "right" },
        { header: "Взвешенная", numeric: true, align: "right" },
        { header: "Достоверность", align: "right" },
      ]}
      rows={breakdown.map((b) => [
        b.title || b.criterion,
        String(b.score),
        String(b.weight),
        String(b.weighted_score),
        b.confidence ?? "—",
      ])}
    />
  );
}
