import type { ComparedMetric, ComparedCountry } from "../../shared/api/cii";

type Props = {
  metrics: ComparedMetric[];
  countries: ComparedCountry[];
};

const COUNTRY_COLORS = ["#1a6abf", "#b85c00"];

export function CiiMetricCompareBars({ metrics, countries }: Props) {
  return (
    <div className="ciiCompareBars">
      <div className="ciiCompareBarsLegend">
        {countries.map((c, i) => (
          <span key={c.slug} className="ciiBarsLegendItem">
            <span
              className="ciiBarsLegendDot"
              style={{ background: COUNTRY_COLORS[i] ?? "#888" }}
            />
            {c.name}
          </span>
        ))}
      </div>
      {metrics.map((m) => (
        <div key={m.metric_slug} className="ciiBarRow">
          <span className="ciiBarLabel">
            {m.metric_name}
            {m.weight != null && (
              <span className="ciiBarWeight">{Math.round(m.weight * 100)}%</span>
            )}
          </span>
          <div className="ciiBarTrack">
            {(m.values ?? []).map((v, i) => {
              const pct =
                v.effective_value != null ? Math.min(v.effective_value, 100) : 0;
              return (
                <div
                  key={v.country_slug}
                  className="ciiBarItem"
                  title={`${countries[i]?.name ?? v.country_slug}: ${v.effective_value?.toFixed(1) ?? "—"}`}
                >
                  <div
                    className="ciiBarFill"
                    style={{
                      width: `${pct}%`,
                      background: COUNTRY_COLORS[i] ?? "#888",
                    }}
                  />
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
