import { useTranslations } from "next-intl";
import { DataTable } from "@country-decision-atlas/ui";
import type { DecisionRunResponse } from "../../shared/api/decision";

type DecisionBreakdownItem =
  DecisionRunResponse["results"][number]["breakdown"][number];

type DecisionBreakdownProps = {
  breakdown: DecisionBreakdownItem[];
};

export function DecisionBreakdown({ breakdown }: DecisionBreakdownProps) {
  const t = useTranslations("countryScores");
  if (breakdown.length === 0) return null;

  return (
    <DataTable
      columns={[
        { header: t("columnCriterion") },
        { header: t("columnScore"), numeric: true, align: "right" },
        { header: t("columnWeight"), numeric: true, align: "right" },
        { header: t("columnWeighted"), numeric: true, align: "right" },
        { header: t("columnConfidence"), align: "right" },
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
