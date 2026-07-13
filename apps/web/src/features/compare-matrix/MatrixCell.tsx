import { scoreLabelStyle } from "@country-decision-atlas/ui";
import { getPathname } from "../../i18n/navigation";
import type { MatrixCell as MatrixCellType } from "../../shared/api/cii";

type Props = {
  cell: MatrixCellType;
  locale: string;
};

export function MatrixCell({ cell, locale }: Props) {
  const { accent } = scoreLabelStyle(cell.score_label);
  const href = getPathname({
    href: `/countries/${cell.country_slug}`,
    locale,
  });

  return (
    <td
      className="border-warm border p-0"
      style={{
        backgroundColor: `color-mix(in srgb, var(--color-${accent}) 14%, transparent)`,
      }}
      data-testid="compare-matrix-cell"
      data-country={cell.country_slug}
      data-scenario={cell.scenario_slug}
    >
      <a
        href={href}
        className="flex flex-col items-center gap-0.5 px-3 py-2 transition-opacity duration-300 hover:opacity-80"
      >
        <span className="font-display text-c1 text-sm font-bold">
          {cell.cii_score != null ? cell.cii_score.toFixed(1) : "—"}
        </span>
        {cell.confidence_label && cell.confidence_label !== "missing" && (
          <span className="font-mono text-c4 text-[8px] tracking-[0.1em] uppercase">
            {cell.confidence_label}
          </span>
        )}
      </a>
    </td>
  );
}
