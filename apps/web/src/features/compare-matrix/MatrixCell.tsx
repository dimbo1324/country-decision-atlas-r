import type { MatrixCell as MatrixCellType } from "../../shared/api/cii";

type Props = {
  cell: MatrixCellType;
  locale: string;
};

const LABEL_CLASS: Record<string, string> = {
  weak: "matrixCellWeak",
  limited: "matrixCellLimited",
  moderate: "matrixCellModerate",
  strong: "matrixCellStrong",
  excellent: "matrixCellExcellent",
  missing: "matrixCellMissing",
};

export function MatrixCell({ cell, locale }: Props) {
  const cellClass =
    LABEL_CLASS[cell.score_label ?? "missing"] ?? "matrixCellMissing";
  const href = `/countries/${cell.country_slug}?locale=${locale}`;

  return (
    <td
      className={`matrixCell ${cellClass}`}
      data-testid="compare-matrix-cell"
      data-country={cell.country_slug}
      data-scenario={cell.scenario_slug}
    >
      <a
        href={href}
        className="matrixCellLink"
      >
        <span className="matrixCellScore">
          {cell.cii_score != null ? cell.cii_score.toFixed(1) : "—"}
        </span>
        {cell.confidence_label && cell.confidence_label !== "missing" && (
          <span className="matrixCellConfidence">{cell.confidence_label}</span>
        )}
      </a>
    </td>
  );
}
