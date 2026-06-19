"use client";

import { Suspense, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";

import type { CountryListResponse } from "../../shared/api/countries";
import type { SourceListResponse } from "../../shared/api/sources";
import { countriesApi, sourcesApi } from "../../shared/api";
import { normalizeLocale } from "../../shared/lib/locale";
import { routes } from "../../shared/lib/routes";
import { formatDate } from "../../shared/lib/format";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";
import { SummaryCard } from "../../shared/ui/SummaryCard";
import { ConfidenceBadge } from "../../shared/ui/ConfidenceBadge";
import { StatusBadge } from "../../shared/ui/StatusBadge";
import { Badge } from "../../shared/ui/Badge";

type ViewError =
  | { error?: { code?: string; message?: string } }
  | string
  | null;

type ConfidenceFilter = "" | "high" | "medium" | "low";

const CONFIDENCE_OPTIONS: ConfidenceFilter[] = ["high", "medium", "low"];

const SOURCE_TYPES = [
  "government",
  "news",
  "academic",
  "ngo",
  "legal",
  "official",
  "other",
];

function SourcesViewInner() {
  const searchParams = useSearchParams();
  const locale = normalizeLocale(searchParams.get("locale"));

  const [countries, setCountries] = useState<CountryListResponse | null>(null);
  const [sources, setSources] = useState<SourceListResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<ViewError>(null);

  const [countrySlug, setCountrySlug] = useState(
    () => searchParams.get("country_slug") ?? "",
  );
  const [sourceType, setSourceType] = useState(
    () => searchParams.get("source_type") ?? "",
  );
  const [confidence, setConfidence] = useState<ConfidenceFilter>(
    () => (searchParams.get("confidence") ?? "") as ConfidenceFilter,
  );

  const countriesById = useMemo(
    () => new Map(countries?.items.map((c) => [c.id, c]) ?? []),
    [countries],
  );

  useEffect(() => {
    let cancelled = false;
    countriesApi
      .listCountries({ locale })
      .then((c) => {
        if (!cancelled) setCountries(c);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [locale]);

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    setError(null);
    sourcesApi
      .listSources({
        locale,
        countrySlug: countrySlug || undefined,
        sourceType: sourceType || undefined,
        confidence: confidence === "" ? undefined : confidence,
        status: "published",
      })
      .then((data) => {
        if (!cancelled) {
          setSources(data);
          setIsLoading(false);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : (err as { error?: { code?: string; message?: string } }),
          );
          setIsLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [locale, countrySlug, sourceType, confidence]);

  const hasFilters = !!(countrySlug || sourceType || confidence);

  function clearFilters() {
    setCountrySlug("");
    setSourceType("");
    setConfidence("");
  }

  return (
    <div className="filterPageWrap">
      <div className="filterBar">
        <div className="filterGroup">
          <label className="filterLabel" htmlFor="src-country">Country</label>
          <select
            id="src-country"
            className="filterSelect"
            value={countrySlug}
            onChange={(e) => setCountrySlug(e.target.value)}
          >
            <option value="">All countries</option>
            {countries?.items.map((c) => (
              <option key={c.slug} value={c.slug}>
                {c.name}
              </option>
            ))}
          </select>
        </div>
        <div className="filterGroup">
          <label className="filterLabel" htmlFor="src-type">Source type</label>
          <select
            id="src-type"
            className="filterSelect"
            value={sourceType}
            onChange={(e) => setSourceType(e.target.value)}
          >
            <option value="">All types</option>
            {SOURCE_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </div>
        <div className="filterGroup">
          <label className="filterLabel" htmlFor="src-confidence">Confidence</label>
          <select
            id="src-confidence"
            className="filterSelect"
            value={confidence}
            onChange={(e) => setConfidence(e.target.value as ConfidenceFilter)}
          >
            <option value="">All confidence</option>
            {CONFIDENCE_OPTIONS.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>
        {hasFilters && (
          <button className="clearButton" onClick={clearFilters}>
            Clear filters
          </button>
        )}
      </div>

      {hasFilters && (
        <div className="activeFilters">
          {countrySlug && (
            <span className="activeFilterChip">country: {countrySlug}</span>
          )}
          {sourceType && (
            <span className="activeFilterChip">type: {sourceType}</span>
          )}
          {confidence && (
            <span className="activeFilterChip">confidence: {confidence}</span>
          )}
        </div>
      )}

      {isLoading && <LoadingState message="Loading sources…" />}
      {!isLoading && error !== null && <ErrorState error={error} />}
      {!isLoading && error === null && sources !== null && (
        <>
          <div className="analyticalSummaryRow">
            <SummaryCard label="Sources shown" value={sources.items.length} />
            <SummaryCard label="Total" value={sources.pagination.total} />
            <SummaryCard
              label="Locale"
              value={sources.locale.resolved_locale}
              detail={sources.locale.translation_status}
            />
          </div>

          {sources.items.length === 0 ? (
            <EmptyState message="No sources match the selected filters." />
          ) : (
            <div className="sourceList">
              {sources.items.map((source) => {
                const country = source.country_id
                  ? countriesById.get(source.country_id)
                  : undefined;
                return (
                  <div key={source.id} className="sourceCard">
                    <div className="sourceCardHeader">
                      <span className="sourceTitle">{source.title}</span>
                      <div className="metaRow">
                        {source.source_type && (
                          <Badge variant="info">{source.source_type}</Badge>
                        )}
                        {source.confidence && (
                          <ConfidenceBadge confidence={source.confidence} />
                        )}
                        {source.language && (
                          <Badge variant="default">{source.language}</Badge>
                        )}
                        {source.status && (
                          <StatusBadge status={source.status} />
                        )}
                      </div>
                    </div>
                    {source.publisher && (
                      <span className="sourcePublisher">{source.publisher}</span>
                    )}
                    <div className="metaRow">
                      {source.last_checked_at && (
                        <span className="metaChip">
                          Checked: {formatDate(source.last_checked_at)}
                        </span>
                      )}
                      {source.published_at && (
                        <span className="metaChip">
                          Published: {formatDate(source.published_at)}
                        </span>
                      )}
                    </div>
                    <div className="cardActions">
                      <a
                        href={source.url}
                        target="_blank"
                        rel="noreferrer"
                        className="externalLink"
                      >
                        Open official source ↗
                      </a>
                      {country && (
                        <Link
                          href={routes.countryWithLocale(country.slug, locale)}
                          className="internalLink"
                        >
                          View {country.name} →
                        </Link>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}
    </div>
  );
}

export function SourcesView() {
  return (
    <Suspense fallback={<LoadingState message="Loading sources…" />}>
      <SourcesViewInner />
    </Suspense>
  );
}
