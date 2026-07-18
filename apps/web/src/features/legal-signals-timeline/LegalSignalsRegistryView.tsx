"use client";

import { useQuery } from "@tanstack/react-query";
import { ChartFrame, LegalSignalTimeline } from "@country-decision-atlas/ui";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@country-decision-atlas/ui";
import { parseAsString, parseAsStringEnum, useQueryState } from "nuqs";
import { Suspense, useState } from "react";
import { countryListQuery } from "../../entities/country/api";
import { legalSignalTimelineQuery } from "../../entities/legal-signals/api";
import { useAppLocale } from "../../shared/lib/useAppLocale";
import { toApiLocale } from "../../shared/lib/locale";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";
import { adaptTimelineEvents } from "./adaptTimelineEvents";
import { LegalSignalEvidenceDrawer } from "./LegalSignalEvidenceDrawer";
import { TimelineEmptyState } from "./TimelineEmptyState";
import { TimelineFilters, type TimelineFilterValues } from "./TimelineFilters";
import { TimelineLegend } from "./TimelineLegend";
import { TimelineYearGroup } from "./TimelineYearGroup";

const VIEW_IDS = ["feed", "timeline"] as const;
type ViewId = (typeof VIEW_IDS)[number];

const VIEW_LABELS: Record<ViewId, string> = {
  feed: "Лента",
  timeline: "Таймлайн",
};

/** One data-fetch, one filter bar, two presentations (year-group feed and
 * a horizontal chart) switched via a tab -- previously two separate pages
 * (`/legal-signals` and `/legal-signals/timeline`) each duplicated the
 * exact same 5 filter query-states and re-fetched the exact same query. */
function LegalSignalsRegistryViewInner() {
  const locale = useAppLocale();
  const apiLocale = toApiLocale(locale);
  const [view, setView] = useQueryState(
    "tab",
    parseAsStringEnum<ViewId>([...VIEW_IDS]).withDefault("feed"),
  );
  const [countrySlug, setCountrySlug] = useQueryState(
    "country_slug",
    parseAsString.withDefault(""),
  );
  const [signalType, setSignalType] = useQueryState(
    "signal_type",
    parseAsString.withDefault(""),
  );
  const [impactDirection, setImpactDirection] = useQueryState(
    "impact_direction",
    parseAsString.withDefault(""),
  );
  const [impactLevel, setImpactLevel] = useQueryState(
    "impact_level",
    parseAsString.withDefault(""),
  );
  const [year, setYear] = useQueryState("year", parseAsString.withDefault(""));
  const [evidenceSignal, setEvidenceSignal] = useState<{
    id: string;
    title: string;
  } | null>(null);

  const filters: TimelineFilterValues = {
    countrySlug,
    signalType,
    impactDirection,
    impactLevel,
    year,
  };

  const { data: countries } = useQuery(
    countryListQuery(locale, { limit: 100 }),
  );
  const {
    data: timeline,
    isPending,
    isError,
  } = useQuery(
    legalSignalTimelineQuery(apiLocale, {
      countrySlug: countrySlug || undefined,
      signalType: signalType || undefined,
      impactDirection: impactDirection || undefined,
      impactLevel: impactLevel || undefined,
      yearFrom: year ? Number(year) : undefined,
      yearTo: year ? Number(year) : undefined,
      limit: 100,
    }),
  );

  function updateFilter(name: keyof TimelineFilterValues, value: string) {
    const setters: Record<
      keyof TimelineFilterValues,
      (v: string | null) => void
    > = {
      countrySlug: (v) => void setCountrySlug(v),
      signalType: (v) => void setSignalType(v),
      impactDirection: (v) => void setImpactDirection(v),
      impactLevel: (v) => void setImpactLevel(v),
      year: (v) => void setYear(v),
    };
    setters[name](value || null);
  }

  const chartEvents = timeline
    ? adaptTimelineEvents(timeline.groups.flatMap((group) => group.events))
    : [];

  return (
    <div className="flex flex-col gap-6">
      <p className="text-c3 max-w-2xl text-sm leading-relaxed">
        Временная карта правовых, миграционных, политических и деловых
        изменений.
      </p>
      <TimelineFilters
        filters={filters}
        countries={countries?.items ?? []}
        years={timeline?.available_years ?? []}
        onChange={updateFilter}
      />
      <TimelineLegend />

      {isError && (
        <ErrorState error="Не удалось загрузить ленту правовых сигналов." />
      )}
      {isPending && !isError && (
        <LoadingState message="Загрузка временной карты изменений…" />
      )}

      {!isPending && !isError && timeline && (
        <Tabs
          value={view}
          onValueChange={(value) => void setView(value as ViewId)}
        >
          <TabsList>
            {VIEW_IDS.map((viewId) => (
              <TabsTrigger
                key={viewId}
                value={viewId}
                data-testid={`legal-signals-view-${viewId}`}
              >
                {VIEW_LABELS[viewId]}
              </TabsTrigger>
            ))}
          </TabsList>

          <TabsContent
            value="feed"
            data-testid="legal-signals-view-panel-feed"
          >
            {timeline.groups.length === 0 ? (
              <TimelineEmptyState />
            ) : (
              <div
                className="flex flex-col gap-8"
                data-testid="legal-signals-timeline"
              >
                <div className="font-mono text-c3 text-[10px] tracking-[0.15em] uppercase">
                  Событий: {timeline.total}
                </div>
                {timeline.groups.map((group) => (
                  <TimelineYearGroup
                    key={group.year}
                    group={group}
                    locale={apiLocale}
                    onShowEvidence={(id, title) =>
                      setEvidenceSignal({ id, title })
                    }
                  />
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent
            value="timeline"
            data-testid="legal-signals-view-panel-timeline"
          >
            {chartEvents.length === 0 ? (
              <EmptyState message="По выбранным фильтрам событий не найдено." />
            ) : (
              <div data-testid="legal-signals-timeline-chart">
                <ChartFrame
                  title={`События: ${chartEvents.length}`}
                  live={false}
                >
                  <LegalSignalTimeline
                    events={chartEvents}
                    active
                    width={960}
                    height={220}
                  />
                </ChartFrame>
              </div>
            )}
          </TabsContent>
        </Tabs>
      )}

      <LegalSignalEvidenceDrawer
        signalId={evidenceSignal?.id ?? null}
        signalTitle={evidenceSignal?.title}
        onClose={() => setEvidenceSignal(null)}
      />
    </div>
  );
}

export function LegalSignalsRegistryView() {
  return (
    <Suspense
      fallback={<LoadingState message="Загрузка временной карты изменений…" />}
    >
      <LegalSignalsRegistryViewInner />
    </Suspense>
  );
}
