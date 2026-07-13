import { Badge, Card } from "@country-decision-atlas/ui";
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
    <div className="flex flex-col gap-3">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {countries.map((c) => (
          <Card
            key={c.slug}
            interactive={false}
            className="flex flex-col gap-2"
          >
            <span className="text-c2 text-sm font-semibold">{c.name}</span>
            {c.cii_score != null ? (
              <span className="font-display text-gold3 text-2xl font-bold">
                {c.cii_score.toFixed(1)}
              </span>
            ) : (
              <span className="font-display text-c4 text-2xl font-bold">—</span>
            )}
            {c.cii_confidence != null && (
              <Badge variant="trust">{c.cii_confidence}</Badge>
            )}
          </Card>
        ))}
      </div>
      {(formulaVersion != null || aggregationMethod != null) && (
        <p className="text-c4 text-xs">
          {[formulaVersion, aggregationMethod].filter(Boolean).join(" · ")}
        </p>
      )}
    </div>
  );
}
