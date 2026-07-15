"use client";

import { useEffect, useState } from "react";
import { Kicker } from "@country-decision-atlas/ui";

import type { PlatformMetricListResponse } from "../../shared/api/platform-metrics";
import type { LocaleCode } from "../../shared/api/countries";
import { getCountryPlatformMetrics } from "../../shared/api/platform-metrics";
import { PlatformMetricCard } from "./PlatformMetricCard";

type DecisionRiskContextProps = {
  countrySlugs: string[];
  scenarioSlug: string;
  locale: LocaleCode;
};

export function DecisionRiskContext({
  countrySlugs,
  scenarioSlug,
  locale,
}: DecisionRiskContextProps) {
  const [metricsMap, setMetricsMap] = useState<
    Record<string, PlatformMetricListResponse>
  >({});
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    setIsLoading(true);
    Promise.all(
      countrySlugs.map((slug) =>
        getCountryPlatformMetrics(slug, locale, scenarioSlug)
          .then((res) => [slug, res] as const)
          .catch(() => [slug, null] as const),
      ),
    )
      .then((results) => {
        if (isMounted) {
          const map: Record<string, PlatformMetricListResponse> = {};
          for (const [slug, res] of results) {
            if (res !== null) {
              map[slug] = res;
            }
          }
          setMetricsMap(map);
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
  }, [countrySlugs, scenarioSlug, locale]);

  const hasAnyMetrics = Object.values(metricsMap).some(
    (r) => r.items.length > 0,
  );

  if (isLoading || !hasAnyMetrics) {
    return null;
  }

  return (
    <section
      className="flex flex-col gap-4"
      data-testid="decision-risk-context"
    >
      <Kicker>Контекст рисков платформенного интеллекта</Kicker>
      {countrySlugs.map((slug) => {
        const metrics = metricsMap[slug];
        if (!metrics || metrics.items.length === 0) return null;
        return (
          <div
            key={slug}
            className="flex flex-col gap-2"
          >
            <h3 className="text-c2 text-sm font-semibold">{slug}</h3>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {metrics.items.map((metric) => (
                <PlatformMetricCard
                  key={`${slug}-${metric.metric_key}-${metric.scenario_slug}`}
                  metric={metric}
                />
              ))}
            </div>
          </div>
        );
      })}
    </section>
  );
}
