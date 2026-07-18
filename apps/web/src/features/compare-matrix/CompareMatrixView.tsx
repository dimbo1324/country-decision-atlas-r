"use client";

import { useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import { Skeleton } from "@country-decision-atlas/ui";
import { matrixQuery } from "../../entities/decision/api";
import { asSupportedLocale, toApiLocale } from "../../shared/lib/locale";
import { CountryScenarioMatrix } from "./CountryScenarioMatrix";
import { MatrixEmptyState } from "./MatrixEmptyState";
import { MatrixLegend } from "./MatrixLegend";
import { MatrixSummary } from "./MatrixSummary";

type Props = {
  /** The real interface locale (e.g. "es") -- kept as-is for URL building
   * further down in `MatrixCell`. The backend's `LocaleCode` only knows
   * en/ru, so the actual data fetch below maps it through `toApiLocale`
   * rather than casting this value directly. */
  locale: string;
};

export function CompareMatrixView({ locale }: Props) {
  const t = useTranslations("compareMatrix");
  const apiLocale = toApiLocale(asSupportedLocale(locale));
  const { data, isPending, isError } = useQuery(matrixQuery(apiLocale));
  const searchParams = useSearchParams();

  if (isPending) {
    return <Skeleton lines={5} />;
  }

  if (isError || !data) {
    return <MatrixEmptyState message={t("loadError")} />;
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
