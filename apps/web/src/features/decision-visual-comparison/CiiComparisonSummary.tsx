import type { ComparedCountry } from "../../shared/api/cii";

type Props = {
  countries: ComparedCountry[];
  formulaVersion: string | null | undefined;
  aggregationMethod: string | null | undefined;
};

export function CiiComparisonSummary({
  countries,
  formulaVersion,
  aggregationMethod,
}: Props) {
  return (
    <div className="ciiCompareSummary">
      <div className="ciiCompareSummaryRow">
        {countries.map((c) => (
          <div
            key={c.slug}
            className="ciiCompareSummaryCard"
          >
            <span className="ciiCompareSummaryName">{c.name}</span>
            {c.cii_score != null ? (
              <span className="ciiCompareSummaryScore">
                {c.cii_score.toFixed(1)}
              </span>
            ) : (
              <span className="ciiCompareSummaryScore ciiCompareMissing">
                —
              </span>
            )}
            {c.cii_confidence != null && (
              <span className="metaChip">{c.cii_confidence}</span>
            )}
          </div>
        ))}
      </div>
      {(formulaVersion != null || aggregationMethod != null) && (
        <p className="ciiCompareMeta">
          {[formulaVersion, aggregationMethod].filter(Boolean).join(" · ")}
        </p>
      )}
    </div>
  );
}
