"use client";

import { Suspense, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";

import type { CountryListResponse } from "../../shared/api/countries";
import type { LegalSignalListResponse } from "../../shared/api/legal-signals";
import { countriesApi, legalSignalsApi } from "../../shared/api";
import { normalizeLocale } from "../../shared/lib/locale";
import { routes } from "../../shared/lib/routes";
import { formatDate } from "../../shared/lib/format";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";
import { SummaryCard } from "../../shared/ui/SummaryCard";
import { ImpactDirectionBadge, ImpactLevelBadge } from "../../shared/ui/ImpactBadge";
import { ConfidenceBadge } from "../../shared/ui/ConfidenceBadge";
import { StatusBadge } from "../../shared/ui/StatusBadge";

type ViewError =
  | { error?: { code?: string; message?: string } }
  | string
  | null;

const SIGNAL_TYPES = [
  "law",
  "bill",
  "policy",
  "court_decision",
  "administrative_change",
  "political_signal",
  "other",
];

const IMPACT_DIRECTIONS = ["positive", "negative", "neutral", "mixed"];
const IMPACT_LEVELS = ["low", "medium", "high", "critical"];

function LegalSignalsViewInner() {
  const searchParams = useSearchParams();
  const locale = normalizeLocale(searchParams.get("locale"));

  const [countries, setCountries] = useState<CountryListResponse | null>(null);
  const [signals, setSignals] = useState<LegalSignalListResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<ViewError>(null);

  const [countrySlug, setCountrySlug] = useState(
    () => searchParams.get("country_slug") ?? "",
  );
  const [signalType, setSignalType] = useState(
    () => searchParams.get("signal_type") ?? "",
  );
  const [impactDirection, setImpactDirection] = useState(
    () => searchParams.get("impact_direction") ?? "",
  );
  const [impactLevel, setImpactLevel] = useState(
    () => searchParams.get("impact_level") ?? "",
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
    legalSignalsApi
      .listLegalSignals({
        locale,
        countrySlug: countrySlug || undefined,
        signalType: signalType || undefined,
        impactDirection: impactDirection || undefined,
        impactLevel: impactLevel || undefined,
        status: "published",
      })
      .then((data) => {
        if (!cancelled) {
          setSignals(data);
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
  }, [locale, countrySlug, signalType, impactDirection, impactLevel]);

  const hasFilters = !!(
    countrySlug ||
    signalType ||
    impactDirection ||
    impactLevel
  );

  function clearFilters() {
    setCountrySlug("");
    setSignalType("");
    setImpactDirection("");
    setImpactLevel("");
  }

  const isFallback = signals?.locale?.translation_status === "fallback";

  return (
    <div className="filterPageWrap">
      {isFallback && (
        <div className="fallbackBanner">
          {locale === "ru"
            ? "Русский перевод частично отсутствует. Показана английская fallback-версия."
            : "Translation content is missing. Showing fallback language content."}
        </div>
      )}

      <div className="filterBar">
        <div className="filterGroup">
          <label className="filterLabel" htmlFor="ls-country">Country</label>
          <select
            id="ls-country"
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
          <label className="filterLabel" htmlFor="ls-type">Signal type</label>
          <select
            id="ls-type"
            className="filterSelect"
            value={signalType}
            onChange={(e) => setSignalType(e.target.value)}
          >
            <option value="">All types</option>
            {SIGNAL_TYPES.map((t) => (
              <option key={t} value={t}>
                {t.replace(/_/g, " ")}
              </option>
            ))}
          </select>
        </div>
        <div className="filterGroup">
          <label className="filterLabel" htmlFor="ls-direction">Impact direction</label>
          <select
            id="ls-direction"
            className="filterSelect"
            value={impactDirection}
            onChange={(e) => setImpactDirection(e.target.value)}
          >
            <option value="">All directions</option>
            {IMPACT_DIRECTIONS.map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
        </div>
        <div className="filterGroup">
          <label className="filterLabel" htmlFor="ls-level">Impact level</label>
          <select
            id="ls-level"
            className="filterSelect"
            value={impactLevel}
            onChange={(e) => setImpactLevel(e.target.value)}
          >
            <option value="">All levels</option>
            {IMPACT_LEVELS.map((l) => (
              <option key={l} value={l}>
                {l}
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
          {signalType && (
            <span className="activeFilterChip">type: {signalType.replace(/_/g, " ")}</span>
          )}
          {impactDirection && (
            <span className="activeFilterChip">direction: {impactDirection}</span>
          )}
          {impactLevel && (
            <span className="activeFilterChip">level: {impactLevel}</span>
          )}
        </div>
      )}

      {isLoading && <LoadingState message="Loading legal signals…" />}
      {!isLoading && error !== null && <ErrorState error={error} />}
      {!isLoading && error === null && signals !== null && (
        <>
          <div className="analyticalSummaryRow">
            <SummaryCard
              label="Signals shown"
              value={signals.items.length}
            />
            <SummaryCard
              label="Total"
              value={signals.pagination.total}
            />
            <SummaryCard
              label="Locale"
              value={signals.locale.resolved_locale}
              detail={signals.locale.translation_status}
            />
          </div>

          {signals.items.length === 0 ? (
            <EmptyState message="No legal signals match the selected filters." />
          ) : (
            <div className="signalList" data-testid="legal-signals-list">
              {signals.items.map((signal) => {
                const country = countriesById.get(signal.country_id);
                return (
                  <div key={signal.id} className="signalCard">
                    <div className="signalCardHeader">
                      <span className="signalTitle">{signal.title}</span>
                      <span className="metaChip">
                        {signal.signal_type.replace(/_/g, " ")}
                      </span>
                    </div>
                    {signal.summary && (
                      <p className="signalSummary">{signal.summary}</p>
                    )}
                    <div className="metaRow">
                      {signal.impact_direction && (
                        <ImpactDirectionBadge direction={signal.impact_direction} />
                      )}
                      {signal.impact_level && (
                        <ImpactLevelBadge level={signal.impact_level} />
                      )}
                      {signal.confidence && (
                        <ConfidenceBadge confidence={signal.confidence} />
                      )}
                      <StatusBadge status={signal.status} />
                    </div>
                    <div className="metaRow">
                      {signal.published_date && (
                        <span className="metaChip">
                          Published: {formatDate(signal.published_date)}
                        </span>
                      )}
                      {signal.effective_date && (
                        <span className="metaChip">
                          Effective: {formatDate(signal.effective_date)}
                        </span>
                      )}
                    </div>
                    {country && (
                      <div className="entityLinkRow">
                        <Link
                          href={routes.countryWithLocale(country.slug, locale)}
                          className="internalLink"
                        >
                          Open country card: {country.name} →
                        </Link>
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

export function LegalSignalsView() {
  return (
    <Suspense fallback={<LoadingState message="Loading legal signals…" />}>
      <LegalSignalsViewInner />
    </Suspense>
  );
}
