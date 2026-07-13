import { RadarChart } from "@country-decision-atlas/ui";
import type { ComparedMetric, ComparedCountry } from "../../shared/api/cii";

type Props = {
  metrics: ComparedMetric[];
  countries: ComparedCountry[];
};

const COUNTRY_ACCENTS = ["blue", "terra"] as const;

export function CiiCompareSpiderChart({ metrics, countries }: Props) {
  if (metrics.length === 0) return null;

  const axes = metrics.map((m) => m.metric_name);
  const series = countries.map((country, index) => ({
    label: country.name,
    accent: COUNTRY_ACCENTS[index] ?? "gold",
    values: metrics.map((m) => {
      const value = (m.values ?? []).find(
        (mv) => mv.country_slug === country.slug,
      );
      return value?.effective_value ?? 0;
    }),
  }));

  return (
    <div
      className="aspect-square w-full"
      data-testid="cii-spider-chart"
    >
      <RadarChart
        axes={axes}
        series={series}
        active
        mode="static"
      />
    </div>
  );
}
