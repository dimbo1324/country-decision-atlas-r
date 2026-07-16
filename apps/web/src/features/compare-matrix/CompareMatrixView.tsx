"use client";

import { useSearchParams } from "next/navigation";
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
  const searchParams = useSearchParams();

  if (isPending) {
    return <Skeleton lines={5} />;
  }

  if (isError || !data) {
    return (
      <MatrixEmptyState message="Не удалось загрузить матрицу сравнения." />
    );
  }

  const allCountries = data.countries ?? [];
  const scenarios = data.scenarios ?? [];
  const cells = data.cells ?? [];

  // Optional pre-fill from the decision results page: /compare?countries=
  // slug1,slug2 narrows the matrix to just those countries. Unknown slugs
  // are dropped rather than erroring; an empty/missing param shows every
  // country, matching the page's original, unfiltered behavior.
  const requestedSlugs = searchParams
    .get("countries")
    ?.split(",")
    .map((slug) => slug.trim())
    .filter(Boolean);
  const countries =
    requestedSlugs && requestedSlugs.length > 0
      ? allCountries.filter((country) => requestedSlugs.includes(country.slug))
      : allCountries;

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
