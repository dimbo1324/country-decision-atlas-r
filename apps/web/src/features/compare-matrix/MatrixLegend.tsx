import { useTranslations } from "next-intl";
import { scoreLabelStyle } from "@country-decision-atlas/ui";

const BAND_KEYS = [
  { label: "weak", key: "bandWeak" },
  { label: "limited", key: "bandLimited" },
  { label: "moderate", key: "bandModerate" },
  { label: "strong", key: "bandStrong" },
  { label: "excellent", key: "bandExcellent" },
];

export function MatrixLegend() {
  const t = useTranslations("compareMatrix");
  return (
    <div
      className="flex flex-col gap-3"
      data-testid="compare-matrix-legend"
    >
      <h3 className="font-mono text-c4 text-[9px] tracking-[0.2em] uppercase">
        {t("legendTitle")}
      </h3>
      <div className="flex flex-wrap gap-4">
        {BAND_KEYS.map((b) => {
          const { accent } = scoreLabelStyle(b.label);
          return (
            <div
              key={b.label}
              className="flex items-center gap-2"
            >
              <span
                className="h-2.5 w-2.5 rounded-full"
                style={{ backgroundColor: `var(--color-${accent})` }}
              />
              <span className="text-c3 text-xs">{t(b.key)}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
