"use client";

import { useQuery } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
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
import { DATE_FORMAT_LOCALE } from "../../shared/lib/format";
import type { SupportedLocale } from "../../shared/lib/locale";
import { useAppLocale } from "../../shared/lib/useAppLocale";
import { HomeDeck } from "./HomeDeck";

function formatGeneratedAt(
  value: string | null | undefined,
  locale: SupportedLocale,
): string {
  if (!value) return "—";
  return new Date(value).toLocaleString(DATE_FORMAT_LOCALE[locale], {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function HomeOverviewView() {
  const t = useTranslations("home");
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
    { value: countriesSummary.length, label: t("statCountries") },
    { value: scenarioWinners.length, label: t("statScenarioWinners") },
    { value: latestLegalEvents.length, label: t("statFreshSignals") },
    { value: keyInsights.length, label: t("statKeyInsights") },
  ];

  return (
    <div
      className="flex flex-col gap-16"
      data-testid="home-overview"
    >
      <section className="flex flex-col items-center gap-6 pt-6 pb-4 text-center">
        <Kicker>
          {t("kicker", {
            date: formatGeneratedAt(overview?.generated_at, locale),
            status: isPending ? t("statusLoading") : t("statusOnline"),
          })}
        </Kicker>
        <h1 className="text-shimmer font-display py-2 text-5xl leading-[1.15] font-bold sm:text-6xl lg:text-7xl">
          Country Decision Atlas
        </h1>
        <p className="font-body text-c2 max-w-2xl text-lg italic sm:text-xl">
          {t("subtitle")}
        </p>

        <div className="mt-2 flex flex-wrap items-center justify-center gap-3">
          <Link href="/decision">
            <Button variant="primary">
              <Compass
                width={14}
                height={14}
                strokeWidth={1.5}
              />
              {t("startDecision")}
            </Button>
          </Link>
          <Link href="/compare">
            <Button variant="ghost">
              <Grid3x3
                width={13}
                height={13}
                strokeWidth={1.5}
              />
              {t("openMatrix")}
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
          title={t("overviewErrorTitle")}
          message={t("overviewErrorMessage")}
        />
      )}
      {isPending && <LoadingState message={t("overviewLoading")} />}
      {isEmpty && <EmptyState message={t("overviewEmpty")} />}
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
            aria-label={t("quickLinksLabel")}
          >
            <Link
              href={overview.links?.countries_url ?? "/countries"}
              className="font-mono text-c3 hover:text-gold3 text-[10px] tracking-[0.2em] uppercase transition-colors duration-300"
            >
              {t("goToCountries")}
            </Link>
            <Link
              href={overview.links?.decision_url ?? "/decision"}
              className="font-mono text-c3 hover:text-gold3 text-[10px] tracking-[0.2em] uppercase transition-colors duration-300"
            >
              {t("runDecision")}
            </Link>
            <Link
              href={overview.links?.compare_url ?? "/compare"}
              className="font-mono text-c3 hover:text-gold3 text-[10px] tracking-[0.2em] uppercase transition-colors duration-300"
            >
              {t("openMatrix")}
            </Link>
            <Link
              href={overview.links?.legal_signals_url ?? "/legal-signals"}
              className="font-mono text-c3 hover:text-gold3 text-[10px] tracking-[0.2em] uppercase transition-colors duration-300"
            >
              {t("openLegalSignals")}
            </Link>
          </nav>
        </>
      )}
    </div>
  );
}
