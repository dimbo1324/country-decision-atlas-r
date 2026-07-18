import { useTranslations } from "next-intl";
import { DataTable } from "@country-decision-atlas/ui";
import type { CountryReadModelResponse } from "../../shared/api/countries";
import { ArrowExternal } from "../../shared/ui/LinkArrow";

type ScoreBreakdownItem = NonNullable<
  CountryReadModelResponse["scores"][number]["breakdowns"]
>[number];

type CountryReadModelSource = CountryReadModelResponse["sources"][number];

type ScoreBreakdownProps = {
  breakdowns: ScoreBreakdownItem[];
  sourcesById?: Map<string, CountryReadModelSource>;
};

export function ScoreBreakdown({
  breakdowns,
  sourcesById,
}: ScoreBreakdownProps) {
  const t = useTranslations("countryScores");
  const linkedSources: CountryReadModelSource[] = [];
  if (sourcesById) {
    const seen = new Set<string>();
    for (const b of breakdowns) {
      for (const sid of b.source_ids ?? []) {
        if (!seen.has(sid)) {
          seen.add(sid);
          const s = sourcesById.get(sid);
          if (s) linkedSources.push(s);
        }
      }
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <DataTable
        columns={[
          { header: t("columnCriterion") },
          { header: t("columnScore"), numeric: true, align: "right" },
          { header: t("columnWeight"), numeric: true, align: "right" },
          { header: t("columnWeighted"), numeric: true, align: "right" },
          { header: t("columnConfidence"), align: "right" },
        ]}
        rows={breakdowns.map((b) => [
          b.criterion,
          String(b.score),
          String(b.weight),
          String(b.weighted_score),
          b.confidence ?? "—",
        ])}
      />

      {linkedSources.length > 0 && (
        <div
          className="flex flex-col gap-2"
          data-testid="supporting-sources"
        >
          <p className="font-mono text-c4 text-[9px] tracking-[0.2em] uppercase">
            {t("supportingSources")}
          </p>
          {linkedSources.map((s) => (
            <div
              key={s.id}
              className="border-warm flex flex-col gap-1 border-l-2 pl-3"
            >
              <span className="text-c2 text-sm">{s.title}</span>
              <div className="flex flex-wrap gap-2">
                {s.source_type && (
                  <span className="font-mono text-c4 text-[8px] tracking-[0.15em] uppercase">
                    {s.source_type}
                  </span>
                )}
                {s.confidence && (
                  <span className="font-mono text-c4 text-[8px] tracking-[0.15em] uppercase">
                    {t("confidenceInline", { value: s.confidence })}
                  </span>
                )}
              </div>
              <a
                href={s.url}
                target="_blank"
                rel="noreferrer"
                className="text-gold3 hover:text-gold text-xs transition-colors duration-300"
              >
                {t("openSource")} <ArrowExternal />
              </a>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
