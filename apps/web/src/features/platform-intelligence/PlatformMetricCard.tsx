import { Badge, Card } from "@country-decision-atlas/ui";
import type { PlatformMetric } from "../../shared/api/platform-metrics";
import { PlatformMetricLabelBadge } from "./PlatformMetricLabelBadge";

const METRIC_NAMES: Record<string, string> = {
  legal_velocity_index: "Индекс правовой динамики",
  scenario_specific_risk_score: "Риск по сценарию",
  contradiction_score: "Оценка противоречий",
};

type PlatformMetricCardProps = {
  metric: PlatformMetric;
};

export function PlatformMetricCard({ metric }: PlatformMetricCardProps) {
  const isInsufficient = metric.label === "insufficient_data";
  const metricName = METRIC_NAMES[metric.metric_key] ?? metric.metric_key;

  return (
    <div
      data-testid="platform-metric-card"
      data-metric-key={metric.metric_key}
    >
      <Card
        interactive={false}
        className="flex flex-col gap-3"
      >
        <div className="flex items-center justify-between gap-2">
          <span className="font-display text-sm font-semibold">
            {metricName}
          </span>
          {metric.scenario_slug && (
            <Badge variant="default">{metric.scenario_slug}</Badge>
          )}
        </div>
        <div className="flex items-center gap-3">
          {isInsufficient ? (
            <span
              className="text-c4 text-sm"
              data-testid="platform-metric-insufficient"
            >
              Недостаточно данных
            </span>
          ) : (
            <span
              className="font-display text-gold3 text-2xl font-bold"
              data-testid="platform-metric-value"
            >
              {metric.value !== null && metric.value !== undefined
                ? Math.round(metric.value)
                : "—"}
            </span>
          )}
          <PlatformMetricLabelBadge label={metric.label} />
        </div>
        <div className="flex flex-wrap gap-2">
          <Badge variant="trust">{metric.confidence}</Badge>
          <Badge variant="default">{metric.freshness_status}</Badge>
        </div>
      </Card>
    </div>
  );
}
