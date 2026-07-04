"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { homeApi, type HomeOverviewResponse } from "../../shared/api/home";
import { resolveLocale } from "../../shared/lib/locale";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";
import { CountryOverviewCards } from "./CountryOverviewCards";
import { HomeMatrixPreview } from "./HomeMatrixPreview";
import { HomeOverviewEmptyState } from "./HomeOverviewEmptyState";
import { KeyInsightsPanel } from "./KeyInsightsPanel";
import { LatestLegalEventsPanel } from "./LatestLegalEventsPanel";
import { ScenarioWinnersPanel } from "./ScenarioWinnersPanel";

function HomeOverviewViewInner() {
  const searchParams = useSearchParams();
  const locale = resolveLocale(searchParams.get("locale"));
  const [overview, setOverview] = useState<HomeOverviewResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setOverview(null);
    setError(null);
    homeApi
      .getOverview({ locale })
      .then((result) => {
        if (active) setOverview(result);
      })
      .catch(() => {
        if (active) setError("Не удалось загрузить аналитический обзор.");
      });
    return () => {
      active = false;
    };
  }, [locale]);

  const countriesSummary = overview?.countries_summary ?? [];
  const scenarioWinners = overview?.scenario_winners ?? [];
  const latestLegalEvents = overview?.latest_legal_events ?? [];
  const keyInsights = overview?.key_insights ?? [];
  const matrixCells = overview?.matrix_preview.cells ?? [];
  const isEmpty =
    overview != null &&
    countriesSummary.length === 0 &&
    matrixCells.length === 0 &&
    latestLegalEvents.length === 0;

  return (
    <div
      className="homeOverview"
      data-testid="home-overview"
    >
      <section className="homeHero">
        <p className="eyebrow">Аналитический обзор MVP</p>
        <h1>Country Decision Atlas</h1>
        <p className="heroSubtitle">
          Сравните страны по сценариям, индексам CII и правовым сигналам.
        </p>
        <div className="homeActions">
          <Link
            href={`/decision?locale=${locale}`}
            className="homeActionPrimary"
          >
            Запустить подбор
          </Link>
          <Link
            href={`/compare?locale=${locale}`}
            className="homeActionSecondary"
          >
            Открыть матрицу
          </Link>
        </div>
      </section>

      {error && <ErrorState error={error} />}
      {!error && !overview && (
        <LoadingState message="Загрузка аналитического обзора…" />
      )}
      {isEmpty && <HomeOverviewEmptyState />}
      {overview && !isEmpty && (
        <>
          <CountryOverviewCards
            countries={countriesSummary}
            locale={locale}
          />
          <ScenarioWinnersPanel winners={scenarioWinners} />
          <HomeMatrixPreview matrix={overview.matrix_preview} />
          <div className="homeOverviewGrid">
            <LatestLegalEventsPanel events={latestLegalEvents} />
            <KeyInsightsPanel insights={keyInsights} />
          </div>
          <nav
            className="homeQuickLinks"
            data-testid="home-quick-links"
            aria-label="Основные разделы"
          >
            <Link
              href={`${overview.links?.countries_url ?? "/countries"}?locale=${locale}`}
            >
              Перейти к странам
            </Link>
            <Link
              href={`${overview.links?.decision_url ?? "/decision"}?locale=${locale}`}
            >
              Запустить decision
            </Link>
            <Link
              href={`${overview.links?.compare_url ?? "/compare"}?locale=${locale}`}
            >
              Открыть матрицу
            </Link>
            <Link
              href={`${overview.links?.legal_signals_url ?? "/legal-signals"}?locale=${locale}`}
            >
              Открыть правовые сигналы
            </Link>
          </nav>
        </>
      )}
    </div>
  );
}

export function HomeOverviewView() {
  return (
    <Suspense
      fallback={<LoadingState message="Загрузка аналитического обзора…" />}
    >
      <HomeOverviewViewInner />
    </Suspense>
  );
}
