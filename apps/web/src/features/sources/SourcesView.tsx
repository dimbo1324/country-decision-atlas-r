"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

import type { CountryListResponse } from "../../shared/api/countries";
import type { SourceListResponse } from "../../shared/api/sources";
import { countriesApi, sourcesApi } from "../../shared/api";
import { normalizeLocale } from "../../shared/lib/locale";
import { formatDate } from "../../shared/lib/format";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";

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

  const [countrySlug, setCountrySlug] = useState("");
  const [sourceType, setSourceType] = useState("");
  const [confidence, setConfidence] = useState<ConfidenceFilter>("");

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

  return (
    <div className="filterPageWrap">
      <div className="filterBar">
        <div className="filterGroup">
          <label className="filterLabel">Country</label>
          <select
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
          <label className="filterLabel">Source type</label>
          <select
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
          <label className="filterLabel">Confidence</label>
          <select
            className="filterSelect"
            value={confidence}
            onChange={(e) =>
              setConfidence(e.target.value as ConfidenceFilter)
            }
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
          <button
            className="clearButton"
            onClick={() => {
              setCountrySlug("");
              setSourceType("");
              setConfidence("");
            }}
          >
            Clear filters
          </button>
        )}
      </div>

      {isLoading && <LoadingState />}
      {!isLoading && error !== null && <ErrorState error={error} />}
      {!isLoading && error === null && sources?.items.length === 0 && (
        <EmptyState />
      )}
      {!isLoading && error === null && sources && sources.items.length > 0 && (
        <>
          <p className="resultCount">
            {sources.items.length} source
            {sources.items.length !== 1 ? "s" : ""}
          </p>
          <div className="sourceList">
            {sources.items.map((source) => (
              <div key={source.id} className="sourceCard">
                <div className="sourceCardHeader">
                  <span className="sourceTitle">{source.title}</span>
                  <div className="metaRow">
                    {source.source_type && (
                      <span className="metaChip">{source.source_type}</span>
                    )}
                    {source.confidence && (
                      <span className="metaChip">{source.confidence}</span>
                    )}
                    {source.language && (
                      <span className="metaChip">{source.language}</span>
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
                <a
                  href={source.url}
                  target="_blank"
                  rel="noreferrer"
                  className="sourceLink"
                >
                  Open source
                </a>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export function SourcesView() {
  return (
    <Suspense fallback={<LoadingState />}>
      <SourcesViewInner />
    </Suspense>
  );
}
