"use client";

import { useEffect, useState } from "react";
import { type CiiCountryComparisonResponse, ciiApi } from "../../shared/api/cii";
import { CiiComparisonEmptyState } from "./CiiComparisonEmptyState";
import { CiiComparisonSummary } from "./CiiComparisonSummary";
import { CiiCompareSpiderChart } from "./CiiCompareSpiderChart";
import { CiiMetricCompareBars } from "./CiiMetricCompareBars";
import { CiiMetricWinnerList } from "./CiiMetricWinnerList";

type Props = {
  countrySlugs: string[];
  scenarioSlug: string;
  locale: string;
};

export function DecisionCiiComparison({ countrySlugs, scenarioSlug, locale }: Props) {
  const [data, setData] = useState<CiiCountryComparisonResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (countrySlugs.length !== 2) {
      setLoading(false);
      return;
    }

    let cancelled = false;
    setLoading(true);
    setError(null);
    setData(null);

    ciiApi
      .compareCountriesCii({ countries: countrySlugs, scenario: scenarioSlug, locale })
      .then((res) => {
        if (!cancelled) {
          setData(res);
          setLoading(false);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setError("Не удалось загрузить данные CII для сравнения");
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [countrySlugs, scenarioSlug, locale]);

  if (countrySlugs.length !== 2) return null;

  if (loading) {
    return (
      <div className="ciiCompareBlock">
        <p className="ciiCompareLoadingText">Загрузка CII-сравнения…</p>
      </div>
    );
  }

  if (error || data == null) {
    return (
      <div className="ciiCompareBlock">
        <CiiComparisonEmptyState message={error ?? undefined} />
      </div>
    );
  }

  const countries = data.countries ?? [];
  const metrics = data.metrics ?? [];
  const { formula_version, aggregation_method } = data;

  if (countries.length === 0 || metrics.length === 0) {
    return (
      <div className="ciiCompareBlock">
        <CiiComparisonEmptyState />
      </div>
    );
  }

  return (
    <section className="ciiCompareBlock" aria-label="CII сравнение стран">
      <h3 className="ciiCompareTitle">
        Сравнение CII: {countries.map((c) => c.name).join(" vs ")}
      </h3>
      <CiiComparisonSummary
        countries={countries}
        formulaVersion={formula_version}
        aggregationMethod={aggregation_method}
      />
      <div className="ciiCompareChartArea">
        <CiiCompareSpiderChart metrics={metrics} countries={countries} />
        <CiiMetricCompareBars metrics={metrics} countries={countries} />
      </div>
      <CiiMetricWinnerList metrics={metrics} countries={countries} />
    </section>
  );
}
