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
      className="platformMetricCard"
      data-testid="platform-metric-card"
      data-metric-key={metric.metric_key}
    >
      <div className="platformMetricHeader">
        <span className="platformMetricName">{metricName}</span>
        {metric.scenario_slug && (
          <span className="platformMetricScenario">{metric.scenario_slug}</span>
        )}
      </div>
      <div className="platformMetricBody">
        {isInsufficient ? (
          <span
            className="platformMetricInsufficient"
            data-testid="platform-metric-insufficient"
          >
            Недостаточно данных
          </span>
        ) : (
          <span
            className="platformMetricValue"
            data-testid="platform-metric-value"
          >
            {metric.value !== null && metric.value !== undefined
              ? Math.round(metric.value)
              : "—"}
          </span>
        )}
        <PlatformMetricLabelBadge label={metric.label} />
      </div>
      <div className="platformMetricMeta">
        <span className="platformMetricConfidence">{metric.confidence}</span>
        <span className="platformMetricFreshness">
          {metric.freshness_status}
        </span>
      </div>
    </div>
  );
}
