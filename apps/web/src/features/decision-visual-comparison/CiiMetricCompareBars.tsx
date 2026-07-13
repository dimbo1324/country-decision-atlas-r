import type { ComparedMetric, ComparedCountry } from "../../shared/api/cii";

type Props = {
  metrics: ComparedMetric[];
  countries: ComparedCountry[];
};

const COUNTRY_COLOR_CLASS = ["bg-blue", "bg-terra"];

export function CiiMetricCompareBars({ metrics, countries }: Props) {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap gap-4">
        {countries.map((c, i) => (
          <span
            key={c.slug}
            className="text-c3 flex items-center gap-2 text-xs"
          >
            <span
              className={`h-2 w-2 rounded-full ${COUNTRY_COLOR_CLASS[i] ?? "bg-c4"}`}
            />
            {c.name}
          </span>
        ))}
      </div>
      {metrics.map((m) => (
        <div
          key={m.metric_slug}
          className="flex flex-col gap-1"
        >
          <span className="font-mono text-c4 flex items-center gap-2 text-[9px] tracking-[0.15em] uppercase">
            {m.metric_name}
            {m.weight != null && (
              <span className="text-c3">{Math.round(m.weight * 100)}%</span>
            )}
          </span>
          <div className="flex flex-col gap-1">
            {(m.values ?? []).map((v, i) => {
              const pct =
                v.effective_value != null
                  ? Math.min(v.effective_value, 100)
                  : 0;
              return (
                <div
                  key={v.country_slug}
                  className="bg-bg4 h-2 w-full"
                  title={`${countries[i]?.name ?? v.country_slug}: ${v.effective_value?.toFixed(1) ?? "—"}`}
                >
                  <div
                    className={`h-full ${COUNTRY_COLOR_CLASS[i] ?? "bg-c4"}`}
                    style={{ width: `${pct}%` }}
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
