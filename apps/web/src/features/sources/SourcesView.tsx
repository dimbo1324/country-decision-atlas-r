"use client";

import { useQuery } from "@tanstack/react-query";
import { Kicker, VirtualList } from "@country-decision-atlas/ui";
import { parseAsString, useQueryState } from "nuqs";
import { Suspense, useMemo, useState } from "react";
import { countryListQuery } from "../../entities/country/api";
import { sourceListQuery } from "../../entities/sources/api";
import { useAppLocale } from "../../shared/lib/useAppLocale";
import { toApiLocale } from "../../shared/lib/locale";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";
import { SourceCard } from "./SourceCard";
import { SourceEvidenceDrawer } from "./SourceEvidenceDrawer";
import { SourcesFilters } from "./SourcesFilters";

function SourcesViewInner() {
  const locale = useAppLocale();
  const [countrySlug, setCountrySlug] = useQueryState(
    "country_slug",
    parseAsString.withDefault(""),
  );
  const [sourceType, setSourceType] = useQueryState(
    "source_type",
    parseAsString.withDefault(""),
  );
  const [confidence, setConfidence] = useQueryState(
    "confidence",
    parseAsString.withDefault(""),
  );
  const [evidenceSource, setEvidenceSource] = useState<{
    id: string;
    title: string;
  } | null>(null);

  const { data: countries } = useQuery(
    countryListQuery(locale, { limit: 100 }),
  );
  const {
    data: sources,
    isPending,
    isError,
  } = useQuery(
    sourceListQuery(toApiLocale(locale), {
      countrySlug: countrySlug || undefined,
      sourceType: sourceType || undefined,
      confidence: (confidence || undefined) as
        | "low"
        | "medium"
        | "high"
        | undefined,
      status: "published",
    }),
  );

  const countriesById = useMemo(
    () => new Map(countries?.items.map((c) => [c.id, c]) ?? []),
    [countries],
  );

  const items = sources?.items ?? [];

  return (
    <div
      className="flex flex-col gap-6"
      data-testid="sources-page"
    >
      <SourcesFilters
        countrySlug={countrySlug}
        sourceType={sourceType}
        confidence={confidence}
        countries={countries?.items ?? []}
        onCountryChange={(v) => void setCountrySlug(v || null)}
        onSourceTypeChange={(v) => void setSourceType(v || null)}
        onConfidenceChange={(v) => void setConfidence(v || null)}
      />

      {sources && (
        <Kicker>
          Источники · {items.length} показано из {sources.pagination.total}
        </Kicker>
      )}

      {isPending && <LoadingState message="Загрузка источников…" />}
      {!isPending && isError && (
        <ErrorState error="Произошла ошибка при загрузке источников." />
      )}
      {!isPending && !isError && items.length === 0 && (
        <EmptyState message="По выбранным фильтрам источники не найдены." />
      )}
      {!isPending && !isError && items.length > 0 && (
        <div data-testid="sources-list">
          <VirtualList
            items={items}
            estimateSize={220}
            renderItem={(source) => (
              <div className="pb-4">
                <SourceCard
                  source={source}
                  country={
                    source.country_id
                      ? countriesById.get(source.country_id)
                      : undefined
                  }
                  onShowEvidence={(id, title) =>
                    setEvidenceSource({ id, title })
                  }
                />
              </div>
            )}
          />
        </div>
      )}

      <SourceEvidenceDrawer
        sourceId={evidenceSource?.id ?? null}
        sourceTitle={evidenceSource?.title}
        onClose={() => setEvidenceSource(null)}
      />
    </div>
  );
}

export function SourcesView() {
  return (
    <Suspense fallback={<LoadingState message="Загрузка источников…" />}>
      <SourcesViewInner />
    </Suspense>
  );
}
