"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { countriesApi, type CountryListResponse } from "../../shared/api/countries";
import { isApiError } from "../../shared/api/http";
import { searchApi, type SearchResponse } from "../../shared/api/search";
import { resolveLocale } from "../../shared/lib/locale";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";
import { SearchFilters } from "./SearchFilters";
import { SearchResultCard } from "./SearchResultCard";

function parseTypes(typesParam: string): string[] {
  return typesParam ? typesParam.split(",").filter(Boolean) : [];
}

function SearchViewInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const locale = resolveLocale(searchParams.get("locale"));
  const q = searchParams.get("q") ?? "";
  const typesParam = searchParams.get("types") ?? "";
  const countrySlugParam = searchParams.get("country_slug") ?? "";

  const [inputValue, setInputValue] = useState(q);
  const [selectedTypes, setSelectedTypes] = useState<string[]>(() =>
    parseTypes(typesParam),
  );
  const [countrySlug, setCountrySlug] = useState(countrySlugParam);
  const [result, setResult] = useState<SearchResponse | null>(null);
  const [countries, setCountries] = useState<CountryListResponse["items"]>([]);
  const [error, setError] = useState<unknown | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    setInputValue(q);
  }, [q]);

  useEffect(() => {
    setSelectedTypes(parseTypes(typesParam));
  }, [typesParam]);

  useEffect(() => {
    setCountrySlug(countrySlugParam);
  }, [countrySlugParam]);

  useEffect(() => {
    countriesApi
      .listCountries({ locale, limit: 100 })
      .then((response) => setCountries(response.items))
      .catch(() => setCountries([]));
  }, [locale]);

  useEffect(() => {
    if (!q.trim()) {
      setResult(null);
      setError(null);
      setIsLoading(false);
      return;
    }
    let active = true;
    setIsLoading(true);
    setError(null);
    searchApi
      .search({
        q,
        locale,
        types: selectedTypes.length > 0 ? selectedTypes.join(",") : undefined,
        countrySlug: countrySlug || undefined,
      })
      .then((response) => {
        if (active) setResult(response);
      })
      .catch((err: unknown) => {
        if (active) {
          setResult(null);
          setError(err);
        }
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });
    return () => {
      active = false;
    };
  }, [q, locale, selectedTypes, countrySlug]);

  function pushParams(next: URLSearchParams) {
    next.set("locale", locale);
    router.push(`/search?${next.toString()}`);
  }

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const next = new URLSearchParams(searchParams.toString());
    const trimmed = inputValue.trim();
    if (trimmed) next.set("q", trimmed);
    else next.delete("q");
    pushParams(next);
  }

  function handleToggleType(type: string) {
    const nextTypes = selectedTypes.includes(type)
      ? selectedTypes.filter((item) => item !== type)
      : [...selectedTypes, type];
    setSelectedTypes(nextTypes);
    const next = new URLSearchParams(searchParams.toString());
    if (nextTypes.length > 0) next.set("types", nextTypes.join(","));
    else next.delete("types");
    pushParams(next);
  }

  function handleCountryChange(nextCountrySlug: string) {
    setCountrySlug(nextCountrySlug);
    const next = new URLSearchParams(searchParams.toString());
    if (nextCountrySlug) next.set("country_slug", nextCountrySlug);
    else next.delete("country_slug");
    pushParams(next);
  }

  const items = result?.items ?? [];

  return (
    <div className="searchPageContainer" data-testid="search-page">
      <form
        className="searchPageForm"
        onSubmit={handleSubmit}
        data-testid="search-page-form"
      >
        <input
          type="search"
          className="searchBoxInput"
          value={inputValue}
          onChange={(event) => setInputValue(event.target.value)}
          placeholder="Поиск по платформе…"
          aria-label="Поиск по платформе"
          data-testid="search-page-input"
        />
        <button
          type="submit"
          className="searchBoxSubmit"
          data-testid="search-page-submit"
        >
          Найти
        </button>
      </form>

      <SearchFilters
        selectedTypes={selectedTypes}
        countrySlug={countrySlug}
        countries={countries}
        onToggleType={handleToggleType}
        onCountryChange={handleCountryChange}
      />

      {!q.trim() && (
        <div className="notice" data-testid="search-prompt">
          Введите запрос, чтобы начать поиск.
        </div>
      )}

      {q.trim() !== "" && isLoading && <LoadingState message="Идёт поиск…" />}

      {q.trim() !== "" && !isLoading && error !== null && (
        <div data-testid="search-error">
          <ErrorState error={isApiError(error) ? error : undefined} />
        </div>
      )}

      {q.trim() !== "" && !isLoading && error === null && result && (
        <>
          <div className="resultCount" data-testid="search-result-count">
            Результатов: {result.total}
          </div>
          {items.length === 0 ? (
            <div className="emptyNotice" data-testid="search-empty-state">
              Ничего не найдено по запросу «{result.query}».
            </div>
          ) : (
            <div className="searchResultList" data-testid="search-result-list">
              {items.map((item) => (
                <SearchResultCard key={item.id} item={item} locale={locale} />
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
