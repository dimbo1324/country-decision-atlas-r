"use client";

import { useQuery } from "@tanstack/react-query";
import { ChartFrame, LegalSignalTimeline } from "@country-decision-atlas/ui";
import { parseAsString, useQueryState } from "nuqs";
import { Suspense } from "react";
import { countryListQuery } from "../../entities/country/api";
import { legalSignalTimelineQuery } from "../../entities/legal-signals/api";
import { useAppLocale } from "../../shared/lib/useAppLocale";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";
import { EmptyState } from "../../shared/ui/EmptyState";
import {
  TimelineFilters,
  type TimelineFilterValues,
} from "../legal-signals-timeline/TimelineFilters";
import { TimelineLegend } from "../legal-signals-timeline/TimelineLegend";
import { adaptTimelineEvents } from "./adaptTimelineEvents";

function LegalSignalsChartViewInner() {
  const locale = useAppLocale();
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
    legalSignalTimelineQuery(locale, {
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

  const events = timeline
    ? adaptTimelineEvents(timeline.groups.flatMap((group) => group.events))
    : [];

  return (
    <div className="flex flex-col gap-6">
      <p className="text-c3 max-w-2xl text-sm leading-relaxed">
        Визуальная шкала времени тех же событий — та же выборка, что и в
        реестре, в виде горизонтальной хронологии.
      </p>
      <TimelineFilters
        filters={filters}
        countries={countries?.items ?? []}
        years={timeline?.available_years ?? []}
        onChange={updateFilter}
      />
      <TimelineLegend />
      {isError && <ErrorState error="Не удалось загрузить временную шкалу." />}
      {isPending && !isError && (
        <LoadingState message="Загрузка временной шкалы…" />
      )}
      {!isPending && !isError && events.length === 0 && (
        <EmptyState message="По выбранным фильтрам событий не найдено." />
      )}
      {!isPending && !isError && events.length > 0 && (
        <div data-testid="legal-signals-timeline-chart">
          <ChartFrame
            title={`События: ${events.length}`}
            live={false}
          >
            <LegalSignalTimeline
              events={events}
              active
              width={960}
              height={220}
            />
          </ChartFrame>
        </div>
      )}
    </div>
  );
}

export function LegalSignalsChartView() {
  return (
    <Suspense fallback={<LoadingState message="Загрузка временной шкалы…" />}>
      <LegalSignalsChartViewInner />
    </Suspense>
  );
}
