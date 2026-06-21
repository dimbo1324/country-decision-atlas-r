"use client";

import { Suspense, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";

import type { CountryListResponse } from "../../shared/api/countries";
import type { SourceListResponse } from "../../shared/api/sources";
import type { EvidenceItem } from "../../shared/api/evidence";
import { countriesApi, sourcesApi, evidenceApi } from "../../shared/api";
import { normalizeLocale } from "../../shared/lib/locale";
import { routes } from "../../shared/lib/routes";
import { formatDate } from "../../shared/lib/format";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";
import { SummaryCard } from "../../shared/ui/SummaryCard";
import { EvidenceCard } from "../../shared/ui/EvidenceCard";
import { ConfidenceBadge } from "../../shared/ui/ConfidenceBadge";
import { StatusBadge } from "../../shared/ui/StatusBadge";
import { Badge } from "../../shared/ui/Badge";

type EvidenceState = EvidenceItem[] | "loading" | "error" | null;

type ViewError = { error?: { code?: string; message?: string } } | string | null;

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

  const [expandedSourceId, setExpandedSourceId] = useState<string | null>(null);
  const [evidenceBySourceId, setEvidenceBySourceId] = useState<
    Record<string, EvidenceState>
  >({});
  const loadedSourceIds = useRef<Set<string>>(new Set());

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
      .catch((err: unknown) => {
        if (!cancelled) setError(err instanceof Error ? err.message : "Ошибка загрузки стран");
      });
    return () => {
      cancelled = true;
    };
  }, [locale]);

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    setError(null);
    setExpandedSourceId(null);
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
              : typeof err === "object" && err !== null && "error" in err
                ? (err as { error?: { code?: string; message?: string } })
                : "Произошла ошибка при загрузке",
          );
          setIsLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [locale, countrySlug, sourceType, confidence]);

  useEffect(() => {
    if (!expandedSourceId) return;
    if (loadedSourceIds.current.has(expandedSourceId)) return;

    loadedSourceIds.current.add(expandedSourceId);
    setEvidenceBySourceId((prev) => ({ ...prev, [expandedSourceId]: "loading" }));

    evidenceApi
      .listEvidenceForSource(expandedSourceId)
      .then((res) => {
        setEvidenceBySourceId((prev) => ({
          ...prev,
          [expandedSourceId]: res.items,
        }));
      })
      .catch(() => {
        loadedSourceIds.current.delete(expandedSourceId);
        setEvidenceBySourceId((prev) => ({
          ...prev,
          [expandedSourceId]: "error",
        }));
      });
  }, [expandedSourceId]);

  function toggleSource(id: string) {
    setExpandedSourceId((prev) => (prev === id ? null : id));
  }

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
          <label className="filterLabel" htmlFor="src-country">
            Страна
          </label>
          <select
            id="src-country"
            className="filterSelect"
            value={countrySlug}
            onChange={(e) => setCountrySlug(e.target.value)}
          >
            <option value="">Все страны</option>
            {countries?.items.map((c) => (
              <option key={c.slug} value={c.slug}>
                {c.name}
              </option>
            ))}
          </select>
        </div>
        <div className="filterGroup">
          <label className="filterLabel" htmlFor="src-type">
            Тип источника
          </label>
          <select
            id="src-type"
            className="filterSelect"
            value={sourceType}
            onChange={(e) => setSourceType(e.target.value)}
          >
            <option value="">Все типы</option>
            {SOURCE_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </div>
        <div className="filterGroup">
          <label className="filterLabel" htmlFor="src-confidence">
            Достоверность
          </label>
          <select
            id="src-confidence"
            className="filterSelect"
            value={confidence}
            onChange={(e) => setConfidence(e.target.value as ConfidenceFilter)}
          >
            <option value="">Все уровни</option>
            {CONFIDENCE_OPTIONS.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>
        {hasFilters && (
          <button className="clearButton" onClick={clearFilters}>
            Сбросить фильтры
          </button>
        )}
      </div>

      {hasFilters && (
        <div className="activeFilters">
          {countrySlug && (
            <span className="activeFilterChip">страна: {countrySlug}</span>
          )}
          {sourceType && <span className="activeFilterChip">тип: {sourceType}</span>}
          {confidence && (
            <span className="activeFilterChip">достоверность: {confidence}</span>
          )}
        </div>
      )}

      {isLoading && <LoadingState message="Загрузка источников…" />}
      {!isLoading && error !== null && <ErrorState error={error} />}
      {!isLoading && error === null && sources !== null && (
        <>
          <div className="analyticalSummaryRow">
            <SummaryCard label="Показано источников" value={sources.items.length} />
            <SummaryCard label="Всего" value={sources.pagination.total} />
            <SummaryCard
              label="Язык"
              value={sources.locale.resolved_locale}
              detail={sources.locale.translation_status}
            />
          </div>

          {sources.items.length === 0 ? (
            <EmptyState message="По выбранным фильтрам источники не найдены." />
          ) : (
            <div className="sourceList" data-testid="sources-list">
              {sources.items.map((source) => {
                const country = source.country_id
                  ? countriesById.get(source.country_id)
                  : undefined;
                const isExpanded = expandedSourceId === source.id;
                const evidence = evidenceBySourceId[source.id];
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
                        {source.status && <StatusBadge status={source.status} />}
                      </div>
                    </div>
                    {source.publisher && (
                      <span className="sourcePublisher">{source.publisher}</span>
                    )}
                    <div className="metaRow">
                      {source.last_checked_at && (
                        <span className="metaChip">
                          Проверено: {formatDate(source.last_checked_at)}
                        </span>
                      )}
                      {source.published_at && (
                        <span className="metaChip">
                          Опубликовано: {formatDate(source.published_at)}
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
                        Открыть источник ↗
                      </a>
                      {country && (
                        <Link
                          href={routes.countryWithLocale(country.slug, locale)}
                          className="internalLink"
                        >
                          Страна: {country.name} →
                        </Link>
                      )}
                      <button
                        className="evidenceToggleBtn"
                        onClick={() => toggleSource(source.id)}
                        data-testid="source-evidence-toggle"
                        aria-expanded={isExpanded}
                      >
                        {isExpanded
                          ? "Скрыть связанные доказательства"
                          : "Показать связанные доказательства"}
                      </button>
                    </div>
                    {isExpanded && (
                      <div className="evidencePanel">
                        {evidence === "loading" && (
                          <LoadingState message="Загрузка связанных доказательств…" />
                        )}
                        {evidence === "error" && (
                          <ErrorState error="Не удалось загрузить связанные доказательства." />
                        )}
                        {Array.isArray(evidence) && evidence.length === 0 && (
                          <EmptyState message="К этому источнику доказательства не прикреплены." />
                        )}
                        {Array.isArray(evidence) && evidence.length > 0 && (
                          <div className="evidenceList">
                            {evidence.map((item) => (
                              <EvidenceCard
                                key={item.id}
                                item={item}
                                sourceTitle={source.title}
                                sourceUrl={source.url}
                              />
                            ))}
                          </div>
                        )}
                      </div>
                    )}
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
    <Suspense fallback={<LoadingState message="Загрузка источников…" />}>
      <SourcesViewInner />
    </Suspense>
  );
}
