"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useMemo, useState } from "react";
import { countriesApi, type CountryListResponse } from "../../shared/api/countries";
import {
  legalSignalsApi,
  type LegalSignalTimelineResponse,
} from "../../shared/api/legal-signals";
import { resolveLocale } from "../../shared/lib/locale";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";
import { TimelineEmptyState } from "./TimelineEmptyState";
import { TimelineFilters, type TimelineFilterValues } from "./TimelineFilters";
import { TimelineLegend } from "./TimelineLegend";
import { TimelineYearGroup } from "./TimelineYearGroup";

function LegalSignalsTimelineViewInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const locale = resolveLocale(searchParams.get("locale"));
  const filters = useMemo<TimelineFilterValues>(
    () => ({
      countrySlug: searchParams.get("country_slug") ?? "",
      signalType: searchParams.get("signal_type") ?? "",
      impactDirection: searchParams.get("impact_direction") ?? "",
      impactLevel: searchParams.get("impact_level") ?? "",
      year: searchParams.get("year") ?? "",
    }),
    [searchParams],
  );
  const [timeline, setTimeline] = useState<LegalSignalTimelineResponse | null>(null);
  const [countries, setCountries] = useState<CountryListResponse["items"]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setTimeline(null);
    setError(null);
    Promise.all([
      legalSignalsApi.getTimeline({
        locale,
        countrySlug: filters.countrySlug,
        signalType: filters.signalType,
        impactDirection: filters.impactDirection,
        impactLevel: filters.impactLevel,
        yearFrom: filters.year ? Number(filters.year) : undefined,
        yearTo: filters.year ? Number(filters.year) : undefined,
      }),
      countriesApi.listCountries({ locale, limit: 100 }),
    ])
      .then(([timelineResult, countriesResult]) => {
        if (active) {
          setTimeline(timelineResult);
          setCountries(countriesResult.items);
        }
      })
      .catch(() => {
        if (active) setError("Не удалось загрузить ленту правовых сигналов.");
      });
    return () => {
      active = false;
    };
  }, [filters, locale]);

  function updateFilter(name: keyof TimelineFilterValues, value: string) {
    const keys: Record<keyof TimelineFilterValues, string> = {
      countrySlug: "country_slug",
      signalType: "signal_type",
      impactDirection: "impact_direction",
      impactLevel: "impact_level",
      year: "year",
    };
    const next = new URLSearchParams(searchParams.toString());
    if (value) next.set(keys[name], value);
    else next.delete(keys[name]);
    next.set("locale", locale);
    router.push(`/legal-signals?${next.toString()}`);
  }

  return (
    <div className="timelineContainer">
      <p className="timelineIntro">
        Временная карта правовых, миграционных, политических и деловых изменений.
      </p>
      <TimelineFilters
        filters={filters}
        countries={countries}
        years={timeline?.available_years ?? []}
        onChange={updateFilter}
      />
      <TimelineLegend />
      {error && <ErrorState error={error} />}
      {!error && !timeline && (
        <LoadingState message="Загрузка временной карты изменений…" />
      )}
      {timeline && timeline.groups.length === 0 && <TimelineEmptyState />}
      {timeline && timeline.groups.length > 0 && (
        <div className="timelineGroups" data-testid="legal-signals-timeline">
          <div className="timelineResultCount">Событий: {timeline.total}</div>
          {timeline.groups.map((group) => (
            <TimelineYearGroup key={group.year} group={group} locale={locale} />
          ))}
        </div>
      )}
    </div>
  );
}

export function LegalSignalsTimelineView() {
  return (
    <Suspense fallback={<LoadingState message="Загрузка временной карты изменений…" />}>
      <LegalSignalsTimelineViewInner />
    </Suspense>
  );
}
