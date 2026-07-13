"use client";

import { useQuery } from "@tanstack/react-query";
import { Kicker, Skeleton } from "@country-decision-atlas/ui";
import { isApiError } from "../../shared/api";
import type { LocaleCode } from "../../shared/api/countries";
import { countryPlatformMetricsQuery } from "../../entities/platform-intelligence/api";
import { ErrorState } from "../../shared/ui/ErrorState";
import { PlatformMetricCard } from "./PlatformMetricCard";
import { PlatformMetricEmptyState } from "./PlatformMetricEmptyState";

type PlatformIntelligenceBlockProps = {
  countrySlug: string;
  locale: LocaleCode;
};

export function PlatformIntelligenceBlock({
  countrySlug,
  locale,
}: PlatformIntelligenceBlockProps) {
  const { data, error, isPending, isError } = useQuery(
    countryPlatformMetricsQuery(countrySlug, locale),
  );

  if (isPending) {
    return <Skeleton lines={4} />;
  }

  if (isError) {
    return (
      <div data-testid="platform-intelligence-error">
        <ErrorState error={isApiError(error) ? error : undefined} />
      </div>
    );
  }

  const items = data?.items ?? [];

  if (items.length === 0) {
    return <PlatformMetricEmptyState />;
  }

  const globalMetrics = items.filter((m) => m.scenario_slug === null);
  const scenarioMetrics = items.filter((m) => m.scenario_slug !== null);

  return (
    <div
      className="flex flex-col gap-6"
      data-testid="platform-intelligence-block"
    >
      {globalMetrics.length > 0 && (
        <div className="flex flex-col gap-3">
          <Kicker>Глобальные показатели</Kicker>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {globalMetrics.map((metric) => (
              <PlatformMetricCard
                key={metric.metric_key}
                metric={metric}
              />
            ))}
          </div>
        </div>
      )}
      {scenarioMetrics.length > 0 && (
        <div className="flex flex-col gap-3">
          <Kicker>Риски по сценариям</Kicker>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {scenarioMetrics.map((metric) => (
              <PlatformMetricCard
                key={`${metric.metric_key}-${metric.scenario_slug}`}
                metric={metric}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
