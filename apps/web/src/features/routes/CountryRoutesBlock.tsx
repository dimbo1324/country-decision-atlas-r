"use client";

import { useEffect, useMemo, useState } from "react";

import { isApiError } from "../../shared/api/http";
import type { LocaleCode } from "../../shared/api/countries";
import type { RouteListResponse } from "../../shared/api/routes";
import { routesApi } from "../../shared/api/routes";
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
  const [filters, setFilters] = useState<RouteFilterValues>(DEFAULT_FILTERS);
  const [data, setData] = useState<RouteListResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const requestParams = useMemo(
    () => ({
      locale,
      route_type: filters.route_type,
      allows_work: filters.allows_work,
      allows_family: filters.allows_family,
      leads_to_pr: filters.leads_to_pr,
      limit: 50,
      offset: 0,
    }),
    [filters, locale],
  );

  useEffect(() => {
    let isMounted = true;
    setIsLoading(true);
    setError(null);
    routesApi
      .listCountryRoutes(countrySlug, requestParams)
      .then((response) => {
        if (isMounted) {
          setData(response);
        }
      })
      .catch((err: unknown) => {
        if (isMounted) {
          const message = isApiError(err)
            ? err.error.message
            : "Маршруты сейчас недоступны.";
          setError(message ?? "Маршруты сейчас недоступны.");
          setData(null);
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
  }, [countrySlug, requestParams]);

  function updateFilter(name: keyof RouteFilterValues, value: string) {
    setFilters((current) => ({ ...current, [name]: value }));
  }

  function resetFilters() {
    setFilters(DEFAULT_FILTERS);
  }

  return (
    <div
      className="routeBlock"
      data-testid="country-routes-block"
    >
      <RouteFilters
        filters={filters}
        onChange={updateFilter}
        onReset={resetFilters}
      />
      {isLoading && <div className="notice">Загрузка маршрутов…</div>}
      {!isLoading && error && <div className="notice errorNotice">{error}</div>}
      {!isLoading && !error && data?.items.length === 0 && <RouteEmptyState />}
      {!isLoading && !error && data && data.items.length > 0 && (
        <>
          {data.pagination.total > data.items.length && (
            <p className="notice">
              Показано {data.items.length} из {data.pagination.total} маршрутов
            </p>
          )}
          <div className="routeGrid">
            {data.items.map((route) => (
              <RouteCard
                key={route.id}
                route={route}
                locale={locale}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
