"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

import type { CountryListResponse } from "../../shared/api/countries";
import type { LegalSignalListResponse } from "../../shared/api/legal-signals";
import { countriesApi, legalSignalsApi } from "../../shared/api";
import { normalizeLocale } from "../../shared/lib/locale";
import { formatDate } from "../../shared/lib/format";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";

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

  const [countrySlug, setCountrySlug] = useState("");
  const [signalType, setSignalType] = useState("");
  const [impactDirection, setImpactDirection] = useState("");
  const [impactLevel, setImpactLevel] = useState("");

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
          <label className="filterLabel">Signal type</label>
          <select
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
          <label className="filterLabel">Impact direction</label>
          <select
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
          <label className="filterLabel">Impact level</label>
          <select
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
          <button
            className="clearButton"
            onClick={() => {
              setCountrySlug("");
              setSignalType("");
              setImpactDirection("");
              setImpactLevel("");
            }}
          >
            Clear filters
          </button>
        )}
      </div>

      {isLoading && <LoadingState />}
      {!isLoading && error !== null && <ErrorState error={error} />}
      {!isLoading && error === null && signals?.items.length === 0 && (
        <EmptyState />
      )}
      {!isLoading && error === null && signals && signals.items.length > 0 && (
        <>
          <p className="resultCount">
            {signals.items.length} signal
            {signals.items.length !== 1 ? "s" : ""}
          </p>
          <div className="signalList">
            {signals.items.map((signal) => (
              <div key={signal.id} className="signalCard">
                <div className="signalCardHeader">
                  <span className="signalTitle">{signal.title}</span>
                  <span className="metaChip">
                    {signal.signal_type.replace(/_/g, " ")}
                  </span>
                </div>
                {signal.summary && <p>{signal.summary}</p>}
                <div className="metaRow">
                  {signal.impact_direction && (
                    <span className="metaChip">
                      Direction: {signal.impact_direction}
                    </span>
                  )}
                  {signal.impact_level && (
                    <span className="metaChip">
                      Level: {signal.impact_level}
                    </span>
                  )}
                  {signal.confidence && (
                    <span className="metaChip">
                      Confidence: {signal.confidence}
                    </span>
                  )}
                  <span className="metaChip">{signal.status}</span>
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
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export function LegalSignalsView() {
  return (
    <Suspense fallback={<LoadingState />}>
      <LegalSignalsViewInner />
    </Suspense>
  );
}
