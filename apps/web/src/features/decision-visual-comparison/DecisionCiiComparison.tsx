"use client";

import { useQuery } from "@tanstack/react-query";
import { Kicker, Skeleton } from "@country-decision-atlas/ui";
import { compareCiiQuery } from "../../entities/decision/api";
import { CiiComparisonEmptyState } from "./CiiComparisonEmptyState";
import { CiiComparisonSummary } from "./CiiComparisonSummary";
import { CiiCompareSpiderChart } from "./CiiCompareSpiderChart";
import { CiiMetricCompareBars } from "./CiiMetricCompareBars";
import { CiiMetricWinnerList } from "./CiiMetricWinnerList";

type Props = {
  countrySlugs: string[];
  scenarioSlug: string;
  locale: string;
  personaSlug?: string | null;
};

export function DecisionCiiComparison({
  countrySlugs,
  scenarioSlug,
  locale,
  personaSlug,
}: Props) {
  const { data, isPending, isError } = useQuery(
    compareCiiQuery({
      countries: countrySlugs,
      scenario: scenarioSlug,
      locale,
      persona: personaSlug,
    }),
  );

  if (countrySlugs.length !== 2) return null;

  if (isPending) {
    return <Skeleton lines={4} />;
  }

  if (isError || data == null) {
    return (
      <CiiComparisonEmptyState message="Не удалось загрузить данные CII для сравнения" />
    );
  }

  const countries = data.countries ?? [];
  const metrics = data.metrics ?? [];
  const { formula_version, aggregation_method } = data;

  if (countries.length === 0 || metrics.length === 0) {
    return <CiiComparisonEmptyState />;
  }

  return (
    <section
      className="flex flex-col gap-5"
      aria-label="CII сравнение стран"
    >
      <div className="flex flex-col gap-1">
        <Kicker>
          Сценарные веса CII: {countries.map((c) => c.name).join(" vs ")}
        </Kicker>
        {data.scenario?.title && (
          <p className="text-c3 text-sm">Сценарий: {data.scenario.title}</p>
        )}
        {data.applied_persona && (
          <p
            className="text-c3 text-sm"
            data-testid="cii-persona-note"
          >
            Персона: {data.applied_persona.name}
          </p>
        )}
      </div>
      <CiiComparisonSummary
        countries={countries}
        formulaVersion={formula_version}
        aggregationMethod={aggregation_method}
      />
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <CiiCompareSpiderChart
          metrics={metrics}
          countries={countries}
        />
        <CiiMetricCompareBars
          metrics={metrics}
          countries={countries}
        />
      </div>
      <CiiMetricWinnerList
        metrics={metrics}
        countries={countries}
      />
    </section>
  );
}
