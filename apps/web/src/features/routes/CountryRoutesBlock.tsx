"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import { Kicker, Skeleton } from "@country-decision-atlas/ui";
import { isApiError } from "../../shared/api/http";
import type { LocaleCode } from "../../shared/api/countries";
import { countryRoutesQuery } from "../../entities/routes/api";
import { ErrorState } from "../../shared/ui/ErrorState";
import { RouteCard } from "./RouteCard";
import { RouteEmptyState } from "./RouteEmptyState";
import { RouteFilters, type RouteFilterValues } from "./RouteFilters";

type CountryRoutesBlockProps = {
  countrySlug: string;
  locale: LocaleCode;
};

const DEFAULT_FILTERS: RouteFilterValues = {
  route_type: "",
  allows_work: "",
  allows_family: "",
  leads_to_pr: "",
};

export function CountryRoutesBlock({
  countrySlug,
  locale,
}: CountryRoutesBlockProps) {
  const t = useTranslations("routes");
  const [filters, setFilters] = useState<RouteFilterValues>(DEFAULT_FILTERS);

  const { data, error, isPending, isError } = useQuery(
    countryRoutesQuery(countrySlug, locale, filters),
  );

  function updateFilter(name: keyof RouteFilterValues, value: string) {
    setFilters((current) => ({ ...current, [name]: value }));
  }

  function resetFilters() {
    setFilters(DEFAULT_FILTERS);
  }

  return (
    <div
      className="flex flex-col gap-5"
      data-testid="country-routes-block"
    >
      <RouteFilters
        filters={filters}
        onChange={updateFilter}
        onReset={resetFilters}
      />
      {isPending && <Skeleton lines={3} />}
      {isError && (
        <ErrorState
          error={
            isApiError(error)
              ? error
              : {
                  error: {
                    code: "unknown",
                    message: t("unavailable"),
                  },
                }
          }
        />
      )}
      {!isPending && !isError && data?.items.length === 0 && (
        <RouteEmptyState />
      )}
      {!isPending && !isError && data && data.items.length > 0 && (
        <>
          {data.pagination.total > data.items.length && (
            <Kicker>
              {t("shownCount", {
                shown: data.items.length,
                total: data.pagination.total,
              })}
            </Kicker>
          )}
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {data.items.map((route) => (
              <RouteCard
                key={route.id}
                route={route}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
