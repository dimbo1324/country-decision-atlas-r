"use client";

import { useQuery } from "@tanstack/react-query";
import {
  Button,
  Counter,
  EmptyState,
  ErrorState,
  Kicker,
  LoadingState,
} from "@country-decision-atlas/ui";
import { Compass, Grid3x3 } from "lucide-react";
import { Link } from "../../i18n/navigation";
import { homeOverviewQuery } from "../../entities/home/api";
import { useAppLocale } from "../../shared/lib/useAppLocale";
import { HomeDeck } from "./HomeDeck";

function formatGeneratedAt(value: string | null | undefined): string {
  if (!value) return "—";
  return new Date(value).toLocaleString("ru-RU", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function HomeOverviewView() {
  const locale = useAppLocale();
  const {
    data: overview,
    isPending,
    isError,
  } = useQuery(homeOverviewQuery(locale));

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

  const stats = [
    { value: countriesSummary.length, label: "Стран в обзоре" },
    { value: scenarioWinners.length, label: "Сценариев с лидером" },
    { value: latestLegalEvents.length, label: "Свежих сигналов" },
    { value: keyInsights.length, label: "Ключевых выводов" },
  ];

  return (
    <div
      className="flex flex-col gap-16"
      data-testid="home-overview"
    >
      <section className="flex flex-col items-center gap-6 pt-6 pb-4 text-center">
        <Kicker>
          Обзор платформы · Обновлено{" "}
          {formatGeneratedAt(overview?.generated_at)}
          {" · "}
          {isPending ? "Загрузка" : "Онлайн"}
        </Kicker>
        <h1 className="text-shimmer font-display py-2 text-5xl leading-[1.15] font-bold sm:text-6xl lg:text-7xl">
          Country Decision Atlas
        </h1>
        <p className="font-body text-c2 max-w-2xl text-lg italic sm:text-xl">
          Сравните страны по сценариям, индексам CII и правовым сигналам.
        </p>

        <div className="mt-2 flex flex-wrap items-center justify-center gap-3">
          <Link href="/decision">
            <Button variant="primary">
              <Compass
                width={14}
                height={14}
                strokeWidth={1.5}
              />
              Запустить подбор
            </Button>
          </Link>
          <Link href="/compare">
            <Button variant="ghost">
              <Grid3x3
                width={13}
                height={13}
                strokeWidth={1.5}
              />
              Открыть матрицу
            </Button>
          </Link>
        </div>

        {!isPending && !isError && (
          <div className="mt-6 flex flex-wrap items-center justify-center gap-x-12 gap-y-6">
            {stats.map((stat) => (
              <div
                key={stat.label}
                className="flex flex-col items-center gap-1"
              >
                <span className="font-display text-gold3 text-4xl font-bold">
                  <Counter
                    value={stat.value}
                    active={overview != null}
                  />
                </span>
                <span className="font-mono text-c3 text-[10px] tracking-[0.2em] uppercase">
                  {stat.label}
                </span>
              </div>
            ))}
          </div>
        )}
      </section>

      {isError && (
        <ErrorState
          title="Обзор недоступен"
          message="Не удалось загрузить аналитический обзор. Попробуйте обновить страницу."
        />
      )}
      {isPending && <LoadingState message="Загрузка аналитического обзора…" />}
      {isEmpty && (
        <EmptyState message="Для аналитического обзора пока недостаточно данных." />
      )}
      {overview && !isEmpty && (
        <>
          <HomeDeck
            countries={countriesSummary}
            scenarioWinners={scenarioWinners}
            matrix={overview.matrix_preview}
            latestLegalEvents={latestLegalEvents}
            keyInsights={keyInsights}
          />
          <nav
            className="border-warm flex flex-wrap items-center justify-center gap-x-10 gap-y-3 border-t pt-8 pb-4"
            data-testid="home-quick-links"
            aria-label="Основные разделы"
          >
            <Link
              href={overview.links?.countries_url ?? "/countries"}
              className="font-mono text-c3 hover:text-gold3 text-[10px] tracking-[0.2em] uppercase transition-colors duration-300"
            >
              Перейти к странам
            </Link>
            <Link
              href={overview.links?.decision_url ?? "/decision"}
              className="font-mono text-c3 hover:text-gold3 text-[10px] tracking-[0.2em] uppercase transition-colors duration-300"
            >
              Запустить decision
            </Link>
            <Link
              href={overview.links?.compare_url ?? "/compare"}
              className="font-mono text-c3 hover:text-gold3 text-[10px] tracking-[0.2em] uppercase transition-colors duration-300"
            >
              Открыть матрицу
            </Link>
            <Link
              href={overview.links?.legal_signals_url ?? "/legal-signals"}
              className="font-mono text-c3 hover:text-gold3 text-[10px] tracking-[0.2em] uppercase transition-colors duration-300"
            >
              Открыть правовые сигналы
            </Link>
          </nav>
        </>
      )}
    </div>
  );
}
