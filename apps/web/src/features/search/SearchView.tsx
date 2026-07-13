"use client";

import { useQuery } from "@tanstack/react-query";
import { ErrorState, LoadingState } from "@country-decision-atlas/ui";
import { parseAsString, useQueryState } from "nuqs";
import { Suspense } from "react";
import {
  COUNTRY_CATALOG_PAGE_SIZE,
  countryListQuery,
} from "../../entities/country/api";
import { searchQuery } from "../../entities/search/api";
import { useAppLocale } from "../../shared/lib/useAppLocale";
import { SearchFilters } from "./SearchFilters";
import { SearchResultCard } from "./SearchResultCard";

function parseTypes(typesParam: string): string[] {
  return typesParam ? typesParam.split(",").filter(Boolean) : [];
}

function SearchViewInner() {
  const locale = useAppLocale();
  const [q, setQ] = useQueryState("q", parseAsString.withDefault(""));
  const [typesParam, setTypesParam] = useQueryState(
    "types",
    parseAsString.withDefault(""),
  );
  const [countrySlug, setCountrySlug] = useQueryState(
    "country_slug",
    parseAsString.withDefault(""),
  );
  const selectedTypes = parseTypes(typesParam);
  const trimmedQuery = q.trim();

  const { data: countries } = useQuery({
    ...countryListQuery(locale, { limit: COUNTRY_CATALOG_PAGE_SIZE }),
  });

  const {
    data: result,
    isFetching,
    isError,
  } = useQuery({
    ...searchQuery({
      q: trimmedQuery,
      locale,
      types: selectedTypes.length > 0 ? selectedTypes.join(",") : undefined,
      countrySlug: countrySlug || undefined,
    }),
    enabled: trimmedQuery.length > 0,
  });

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const nextQuery = String(form.get("q") ?? "").trim();
    void setQ(nextQuery || null);
  }

  function handleToggleType(type: string) {
    const nextTypes = selectedTypes.includes(type)
      ? selectedTypes.filter((item) => item !== type)
      : [...selectedTypes, type];
    void setTypesParam(nextTypes.length > 0 ? nextTypes.join(",") : null);
  }

  function handleCountryChange(nextCountrySlug: string) {
    void setCountrySlug(nextCountrySlug || null);
  }

  const items = result?.items ?? [];

  return (
    <div
      className="flex flex-col gap-6"
      data-testid="search-page"
    >
      <form
        className="border-warm flex border"
        onSubmit={handleSubmit}
        data-testid="search-page-form"
      >
        <input
          type="search"
          name="q"
          defaultValue={q}
          key={q}
          className="text-c1 placeholder:text-c4 font-body w-full bg-transparent px-4 py-3 text-sm outline-none"
          placeholder="Поиск по платформе…"
          aria-label="Поиск по платформе"
          data-testid="search-page-input"
        />
        <button
          type="submit"
          className="font-mono text-c3 hover:text-gold3 border-warm border-l px-5 py-3 text-[10px] tracking-[0.2em] uppercase transition-colors duration-300"
          data-testid="search-page-submit"
        >
          Найти
        </button>
      </form>

      <SearchFilters
        selectedTypes={selectedTypes}
        countrySlug={countrySlug}
        countries={countries?.items ?? []}
        onToggleType={handleToggleType}
        onCountryChange={handleCountryChange}
      />

      {!trimmedQuery && (
        <p
          className="text-c3 text-sm"
          data-testid="search-prompt"
        >
          Введите запрос, чтобы начать поиск.
        </p>
      )}

      {trimmedQuery !== "" && isFetching && (
        <LoadingState message="Идёт поиск…" />
      )}

      {trimmedQuery !== "" && !isFetching && isError && (
        <div data-testid="search-error">
          <ErrorState
            title="Поиск недоступен"
            message="Не удалось выполнить поиск. Попробуйте ещё раз."
          />
        </div>
      )}

      {trimmedQuery !== "" && !isFetching && !isError && result && (
        <>
          <div
            className="font-mono text-c3 text-[10px] tracking-[0.15em] uppercase"
            data-testid="search-result-count"
          >
            Результатов: {result.total}
          </div>
          {items.length === 0 ? (
            <p
              className="text-c3 text-sm"
              data-testid="search-empty-state"
            >
              Ничего не найдено по запросу «{result.query}».
            </p>
          ) : (
            <div
              className="flex flex-col gap-3"
              data-testid="search-result-list"
            >
              {items.map((item) => (
                <SearchResultCard
                  key={item.id}
                  item={item}
                />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}

export function SearchView() {
  return (
    <Suspense fallback={<LoadingState message="Загрузка поиска…" />}>
      <SearchViewInner />
    </Suspense>
  );
}
