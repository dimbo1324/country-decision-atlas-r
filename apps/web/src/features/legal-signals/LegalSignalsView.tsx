"use client";

import { Suspense, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";

import type { CountryListResponse } from "../../shared/api/countries";
import type { LegalSignalListResponse } from "../../shared/api/legal-signals";
import type { EvidenceItem } from "../../shared/api/evidence";
import { countriesApi, legalSignalsApi, evidenceApi } from "../../shared/api";
import { normalizeLocale } from "../../shared/lib/locale";
import { routes } from "../../shared/lib/routes";
import { formatDate } from "../../shared/lib/format";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";
import { SummaryCard } from "../../shared/ui/SummaryCard";
import { EvidenceCard } from "../../shared/ui/EvidenceCard";
import { ImpactDirectionBadge, ImpactLevelBadge } from "../../shared/ui/ImpactBadge";
import { ConfidenceBadge } from "../../shared/ui/ConfidenceBadge";
import { StatusBadge } from "../../shared/ui/StatusBadge";

type ViewError = { error?: { code?: string; message?: string } } | string | null;

type EvidenceState = EvidenceItem[] | "loading" | "error" | null;

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

  const [expandedSignalId, setExpandedSignalId] = useState<string | null>(null);
  const [evidenceBySignalId, setEvidenceBySignalId] = useState<
    Record<string, EvidenceState>
  >({});

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
    setExpandedSignalId(null);
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

  useEffect(() => {
    if (!expandedSignalId) return;
    if (evidenceBySignalId[expandedSignalId] !== undefined) return;

    setEvidenceBySignalId((prev) => ({ ...prev, [expandedSignalId]: "loading" }));

    evidenceApi
      .listEvidenceForLegalSignal(expandedSignalId)
      .then((res) => {
        setEvidenceBySignalId((prev) => ({
          ...prev,
          [expandedSignalId]: res.items,
        }));
      })
      .catch(() => {
        setEvidenceBySignalId((prev) => ({
          ...prev,
          [expandedSignalId]: "error",
        }));
      });
  }, [expandedSignalId, evidenceBySignalId]);

  function toggleSignal(id: string) {
    setExpandedSignalId((prev) => (prev === id ? null : id));
  }

  const hasFilters = !!(countrySlug || signalType || impactDirection || impactLevel);

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
          Русский перевод частично отсутствует. Показана английская fallback-версия.
        </div>
      )}

      <div className="filterBar">
        <div className="filterGroup">
          <label className="filterLabel" htmlFor="ls-country">
            Страна
          </label>
          <select
            id="ls-country"
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
          <label className="filterLabel" htmlFor="ls-type">
            Тип сигнала
          </label>
          <select
            id="ls-type"
            className="filterSelect"
            value={signalType}
            onChange={(e) => setSignalType(e.target.value)}
          >
            <option value="">Все типы</option>
            {SIGNAL_TYPES.map((t) => (
              <option key={t} value={t}>
                {t.replace(/_/g, " ")}
              </option>
            ))}
          </select>
        </div>
        <div className="filterGroup">
          <label className="filterLabel" htmlFor="ls-direction">
            Направление влияния
          </label>
          <select
            id="ls-direction"
            className="filterSelect"
            value={impactDirection}
            onChange={(e) => setImpactDirection(e.target.value)}
          >
            <option value="">Все направления</option>
            {IMPACT_DIRECTIONS.map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
        </div>
        <div className="filterGroup">
          <label className="filterLabel" htmlFor="ls-level">
            Уровень влияния
          </label>
          <select
            id="ls-level"
            className="filterSelect"
            value={impactLevel}
            onChange={(e) => setImpactLevel(e.target.value)}
          >
            <option value="">Все уровни</option>
            {IMPACT_LEVELS.map((l) => (
              <option key={l} value={l}>
                {l}
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
          {signalType && (
            <span className="activeFilterChip">
              тип: {signalType.replace(/_/g, " ")}
            </span>
          )}
          {impactDirection && (
            <span className="activeFilterChip">направление: {impactDirection}</span>
          )}
          {impactLevel && (
            <span className="activeFilterChip">уровень: {impactLevel}</span>
          )}
        </div>
      )}

      {isLoading && <LoadingState message="Загрузка правовых сигналов…" />}
      {!isLoading && error !== null && <ErrorState error={error} />}
      {!isLoading && error === null && signals !== null && (
        <>
          <div className="analyticalSummaryRow">
            <SummaryCard label="Показано сигналов" value={signals.items.length} />
            <SummaryCard label="Всего" value={signals.pagination.total} />
            <SummaryCard
              label="Язык"
              value={signals.locale.resolved_locale}
              detail={signals.locale.translation_status}
            />
          </div>

          {signals.items.length === 0 ? (
            <EmptyState message="По выбранным фильтрам правовые сигналы не найдены." />
          ) : (
            <div className="signalList" data-testid="legal-signals-list">
              {signals.items.map((signal) => {
                const country = countriesById.get(signal.country_id);
                const isExpanded = expandedSignalId === signal.id;
                const evidence = evidenceBySignalId[signal.id];
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
                    {signal.affected_groups && signal.affected_groups.length > 0 && (
                      <div className="metaRow">
                        {signal.affected_groups.map((g) => (
                          <span key={g} className="metaChip">
                            {g}
                          </span>
                        ))}
                      </div>
                    )}
                    <div className="metaRow">
                      {signal.published_date && (
                        <span className="metaChip">
                          Опубликовано: {formatDate(signal.published_date)}
                        </span>
                      )}
                      {signal.effective_date && (
                        <span className="metaChip">
                          Действует с: {formatDate(signal.effective_date)}
                        </span>
                      )}
                    </div>
                    <div className="cardActions">
                      {country && (
                        <Link
                          href={routes.countryWithLocale(country.slug, locale)}
                          className="internalLink"
                        >
                          Карточка страны: {country.name} →
                        </Link>
                      )}
                      <button
                        className="evidenceToggleBtn"
                        onClick={() => toggleSignal(signal.id)}
                        data-testid="legal-signal-evidence-toggle"
                        aria-expanded={isExpanded}
                      >
                        {isExpanded
                          ? "Скрыть доказательства"
                          : "Показать доказательства"}
                      </button>
                    </div>
                    {isExpanded && (
                      <div className="evidencePanel">
                        {evidence === "loading" && (
                          <LoadingState message="Загрузка доказательств…" />
                        )}
                        {evidence === "error" && (
                          <ErrorState error="Не удалось загрузить доказательства." />
                        )}
                        {Array.isArray(evidence) && evidence.length === 0 && (
                          <EmptyState message="Подтверждающие доказательства пока не прикреплены." />
                        )}
                        {Array.isArray(evidence) && evidence.length > 0 && (
                          <div className="evidenceList">
                            {evidence.map((item) => (
                              <EvidenceCard key={item.id} item={item} />
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

export function LegalSignalsView() {
  return (
    <Suspense fallback={<LoadingState message="Загрузка правовых сигналов…" />}>
      <LegalSignalsViewInner />
    </Suspense>
  );
}
