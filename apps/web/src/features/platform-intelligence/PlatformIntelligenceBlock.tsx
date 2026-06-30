"use client";

import { useEffect, useState } from "react";

import { isApiError } from "../../shared/api";
import type { PlatformMetricListResponse } from "../../shared/api/platform-metrics";
import type { LocaleCode } from "../../shared/api/countries";
import { getCountryPlatformMetrics } from "../../shared/api/platform-metrics";
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
  const [data, setData] = useState<PlatformMetricListResponse | null>(null);
  const [error, setError] = useState<unknown | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    setIsLoading(true);
    setError(null);
    getCountryPlatformMetrics(countrySlug, locale)
      .then((res) => {
        if (isMounted) {
          setData(res);
        }
      })
      .catch((err: unknown) => {
        if (isMounted) {
          setData(null);
          setError(err);
        }
      })
      .finally(() => {
        if (isMounted) {
          setIsLoading(false);
        }
      });
    return () => {
      isMounted = false;
    };
  }, [countrySlug, locale]);

  if (isLoading) {
    return <div className="notice">Загрузка данных платформенного интеллекта...</div>;
  }

  if (error !== null) {
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
    <div data-testid="platform-intelligence-block">
      {globalMetrics.length > 0 && (
        <div className="platformMetricGroup">
          <h3 className="platformMetricGroupTitle">Глобальные показатели</h3>
          <div className="platformMetricGrid">
            {globalMetrics.map((metric) => (
              <PlatformMetricCard key={metric.metric_key} metric={metric} />
            ))}
          </div>
        </div>
      )}
      {scenarioMetrics.length > 0 && (
        <div className="platformMetricGroup">
          <h3 className="platformMetricGroupTitle">Риски по сценариям</h3>
          <div className="platformMetricGrid">
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
