import type { ComparedMetric, ComparedCountry } from "../../shared/api/cii";

type Props = {
  metrics: ComparedMetric[];
  countries: ComparedCountry[];
};

export function CiiMetricWinnerList({ metrics, countries }: Props) {
  const nameBySlug = Object.fromEntries(countries.map((c) => [c.slug, c.name]));

  return (
    <ul className="ciiWinnerList">
      {metrics.map((m) => (
        <li
          key={m.metric_slug}
          className="ciiWinnerItem"
        >
          <span className="ciiWinnerMetricName">{m.metric_name}</span>
          <span className="ciiWinnerBadgeWrap">
            {m.winner_country_slug != null ? (
              <span className="metaChip ciiWinnerBadge">
                {nameBySlug[m.winner_country_slug] ?? m.winner_country_slug}
              </span>
            ) : (
              <span className="metaChip ciiWinnerTie">—</span>
            )}
            {m.delta != null && (
              <span className="ciiWinnerDelta">Δ {m.delta.toFixed(1)}</span>
            )}
          </span>
        </li>
      ))}
    </ul>
  );
}
