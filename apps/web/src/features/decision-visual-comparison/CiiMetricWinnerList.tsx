import { Badge } from "@country-decision-atlas/ui";
import type { ComparedMetric, ComparedCountry } from "../../shared/api/cii";

type Props = {
  metrics: ComparedMetric[];
  countries: ComparedCountry[];
};

export function CiiMetricWinnerList({ metrics, countries }: Props) {
  const nameBySlug = Object.fromEntries(countries.map((c) => [c.slug, c.name]));

  return (
    <ul
      className="flex flex-col gap-2"
      data-testid="cii-winner-list"
    >
      {metrics.map((m) => (
        <li
          key={m.metric_slug}
          className="flex items-center justify-between gap-3"
        >
          <span className="text-c3 text-sm">{m.metric_name}</span>
          <span className="flex items-center gap-2">
            {m.winner_country_slug != null ? (
              <Badge variant="trust">
                {nameBySlug[m.winner_country_slug] ?? m.winner_country_slug}
              </Badge>
            ) : (
              <Badge variant="default">—</Badge>
            )}
            {m.delta != null && (
              <span className="text-c4 text-xs">Δ {m.delta.toFixed(1)}</span>
            )}
          </span>
        </li>
      ))}
    </ul>
  );
}
