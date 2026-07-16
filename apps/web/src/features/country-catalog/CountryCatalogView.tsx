"use client";

import { useQuery } from "@tanstack/react-query";
import {
  Card,
  EmptyState,
  ErrorState,
  Kicker,
  LoadingState,
  Pagination,
  Skeleton,
} from "@country-decision-atlas/ui";
import { parseAsInteger, useQueryState } from "nuqs";
import { Suspense } from "react";
import {
  COUNTRY_CATALOG_PAGE_SIZE,
  countryListQuery,
} from "../../entities/country/api";
import { myWatchlistQuery } from "../../entities/watchlist/api";
import { useAuth } from "../../shared/auth/AuthProvider";
import { useAppLocale } from "../../shared/lib/useAppLocale";
import { CountryCatalogCard } from "./CountryCatalogCard";

function CatalogSkeletonGrid() {
  return (
    <div
      className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
      aria-hidden
    >
      {Array.from({ length: 6 }).map((_, index) => (
        <Card
          key={index}
          interactive={false}
        >
          <Skeleton lines={3} />
        </Card>
      ))}
    </div>
  );
}

function CountryCatalogViewInner() {
  const locale = useAppLocale();
  const { user } = useAuth();
  const [page, setPage] = useQueryState("page", parseAsInteger.withDefault(1));
  const offset = (page - 1) * COUNTRY_CATALOG_PAGE_SIZE;

  const { data, isPending, isError } = useQuery(
    countryListQuery(locale, { limit: COUNTRY_CATALOG_PAGE_SIZE, offset }),
  );
  const { data: watchlist } = useQuery({
    ...myWatchlistQuery(),
    enabled: Boolean(user),
  });
  const savedSlugs = new Set(
    (watchlist?.items ?? []).map((item) => item.country_slug),
  );

  const items = data?.items ?? [];
  const total = data?.pagination.total ?? 0;
  const pageCount = Math.max(1, Math.ceil(total / COUNTRY_CATALOG_PAGE_SIZE));

  return (
    <div
      className="flex flex-col gap-8"
      data-testid="country-catalog"
    >
      <header className="flex flex-col gap-3">
        <Kicker>Каталог · {total || "…"} стран</Kicker>
        <h1 className="font-display text-4xl font-bold">
          Карточки стран для подбора
        </h1>
        <p className="text-c3 max-w-2xl text-sm leading-relaxed">
          Каждая карточка страны содержит сценарные оценки, правовые сигналы,
          доказательства с источниками и профильные разделы для принятия
          решений.
        </p>
      </header>

      {isError && (
        <ErrorState
          title="Не удалось загрузить страны"
          message="Произошла ошибка при загрузке каталога. Попробуйте обновить страницу."
        />
      )}

      {isPending && <CatalogSkeletonGrid />}

      {!isPending && !isError && items.length === 0 && (
        <EmptyState message="Страны пока отсутствуют." />
      )}

      {!isPending && !isError && items.length > 0 && (
        <>
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {items.map((country) => (
              <CountryCatalogCard
                key={country.slug}
                country={country}
                saved={savedSlugs.has(country.slug)}
                authenticated={Boolean(user)}
              />
            ))}
          </div>
          <Pagination
            page={page}
            pageCount={pageCount}
            onPageChange={setPage}
          />
        </>
      )}
    </div>
  );
}

export function CountryCatalogView() {
  return (
    <Suspense fallback={<LoadingState message="Загрузка каталога…" />}>
      <CountryCatalogViewInner />
    </Suspense>
  );
}
