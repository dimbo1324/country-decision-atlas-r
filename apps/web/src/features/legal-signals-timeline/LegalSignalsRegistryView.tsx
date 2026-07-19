"use client";

import { useQuery } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import { ChartFrame, LegalSignalTimeline } from "@country-decision-atlas/ui";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@country-decision-atlas/ui";
import { parseAsString, parseAsStringEnum, useQueryState } from "nuqs";
import { Suspense, useState } from "react";
import { allCountriesQuery } from "../../entities/decision/api";
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

const VIEW_LABEL_KEYS: Record<ViewId, string> = {
  feed: "viewFeed",
  timeline: "viewTimeline",
};

/** One data-fetch, one filter bar, two presentations (year-group feed and
 * a horizontal chart) switched via a tab -- previously two separate pages
 * (`/legal-signals` and `/legal-signals/timeline`) each duplicated the
 * exact same 5 filter query-states and re-fetched the exact same query. */
function LegalSignalsRegistryViewInner() {
  const t = useTranslations("legalSignalsTimeline");
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

  const { data: countries } = useQuery(allCountriesQuery(apiLocale));
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
    ? adaptTimelineEvents(
        timeline.groups.flatMap((group) => group.events),
        locale,
      )
    : [];

  return (
    <div className="flex flex-col gap-6">
      <p className="text-c3 max-w-2xl text-sm leading-relaxed">
        {t("description")}
      </p>
      <TimelineFilters
        filters={filters}
        countries={countries?.items ?? []}
        years={timeline?.available_years ?? []}
        onChange={updateFilter}
      />
      <TimelineLegend />

      {isError && <ErrorState error={t("loadError")} />}
      {isPending && !isError && <LoadingState message={t("loading")} />}

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
                {t(VIEW_LABEL_KEYS[viewId])}
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
                  {t("eventsCount", { count: timeline.total })}
                </div>
                {timeline.groups.map((group) => (
                  <TimelineYearGroup
                    key={group.year}
                    group={group}
                    locale={locale}
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
              <EmptyState message={t("noEventsForFilters")} />
            ) : (
              <div data-testid="legal-signals-timeline-chart">
                <ChartFrame
                  title={t("eventsCount", { count: chartEvents.length })}
                  live={false}
                  labels={{
                    verifiedAtTitle: t("chartFrameVerifiedAtTitle"),
                    verifiedAtLabel: t("chartFrameVerifiedAtLabel"),
                    confidenceTitle: t("chartFrameConfidenceTitle"),
                    confidenceLabel: {
                      low: t("chartFrameConfidenceLow"),
                      medium: t("chartFrameConfidenceMedium"),
                      high: t("chartFrameConfidenceHigh"),
                    },
                    live: t("chartFrameLive"),
                    collapseAriaLabel: t("chartFrameCollapseAriaLabel"),
                    expandAriaLabel: t("chartFrameExpandAriaLabel"),
                    expandedPlaceholder: t("chartFrameExpandedPlaceholder"),
                  }}
                >
                  <LegalSignalTimeline
                    events={chartEvents}
                    active
                    width={960}
                    height={220}
                    ariaLabel={t("chartAriaLabel", {
                      count: chartEvents.length,
                    })}
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

function LegalSignalsLoadingFallback() {
  const t = useTranslations("legalSignalsTimeline");
  return <LoadingState message={t("loading")} />;
}

export function LegalSignalsRegistryView() {
  return (
    <Suspense fallback={<LegalSignalsLoadingFallback />}>
      <LegalSignalsRegistryViewInner />
    </Suspense>
  );
}
