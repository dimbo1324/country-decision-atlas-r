"use client";

import { useEffect, useState } from "react";
import type { CompareMatrixResponse } from "../../shared/api/cii";
import { ciiApi } from "../../shared/api/cii";
import { CountryScenarioMatrix } from "./CountryScenarioMatrix";
import { MatrixEmptyState } from "./MatrixEmptyState";
import { MatrixLegend } from "./MatrixLegend";
import { MatrixSummary } from "./MatrixSummary";

type Props = {
  locale: string;
};

export function CompareMatrixView({ locale }: Props) {
  const [data, setData] = useState<CompareMatrixResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    ciiApi
      .getMatrix({ scenarios: "all", locale })
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch(() => {
        setError("Не удалось загрузить матрицу сравнения.");
        setLoading(false);
      });
  }, [locale]);

  if (loading) {
    return (
      <div className="matrixBlock">
        <p className="matrixLoadingText">Загрузка матрицы…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="matrixBlock">
        <MatrixEmptyState message={error} />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="matrixBlock">
        <MatrixEmptyState />
      </div>
    );
  }

  const countries = data.countries ?? [];
  const scenarios = data.scenarios ?? [];
  const cells = data.cells ?? [];

  if (countries.length === 0 || scenarios.length === 0) {
    return (
      <div className="matrixBlock">
        <MatrixEmptyState />
      </div>
    );
  }

  return (
    <div className="matrixBlock" data-testid="compare-matrix-block">
      <CountryScenarioMatrix
        countries={countries}
        scenarios={scenarios}
        cells={cells}
        locale={locale}
      />
      <MatrixLegend />
      <MatrixSummary countries={countries} scenarios={scenarios} cells={cells} />
    </div>
  );
}
