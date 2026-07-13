"use client";

import { useQuery } from "@tanstack/react-query";
import { Skeleton } from "@country-decision-atlas/ui";
import type { components } from "@country-decision-atlas/contracts/generated/types";
import { matrixQuery } from "../../entities/decision/api";
import { CountryScenarioMatrix } from "./CountryScenarioMatrix";
import { MatrixEmptyState } from "./MatrixEmptyState";
import { MatrixLegend } from "./MatrixLegend";
import { MatrixSummary } from "./MatrixSummary";

type LocaleCode = components["schemas"]["LocaleCode"];

type Props = {
  locale: string;
};

export function CompareMatrixView({ locale }: Props) {
  const { data, isPending, isError } = useQuery(
    matrixQuery(locale as LocaleCode),
  );

  if (isPending) {
    return <Skeleton lines={5} />;
  }

  if (isError || !data) {
    return (
      <MatrixEmptyState message="Не удалось загрузить матрицу сравнения." />
    );
  }

  const countries = data.countries ?? [];
  const scenarios = data.scenarios ?? [];
  const cells = data.cells ?? [];

  if (countries.length === 0 || scenarios.length === 0) {
    return <MatrixEmptyState />;
  }

  return (
    <div
      className="flex flex-col gap-6"
      data-testid="compare-matrix-block"
    >
      <CountryScenarioMatrix
        countries={countries}
        scenarios={scenarios}
        cells={cells}
        locale={locale}
      />
      <MatrixLegend />
      <MatrixSummary
        countries={countries}
        scenarios={scenarios}
        cells={cells}
      />
    </div>
  );
}
