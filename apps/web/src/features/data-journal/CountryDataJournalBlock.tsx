"use client";

import { useRef } from "react";
import { useQuery } from "@tanstack/react-query";
import { Skeleton } from "@country-decision-atlas/ui";
import { isApiError } from "../../shared/api";
import type { LocaleCode } from "../../shared/api/countries";
import { countryDataJournalQuery } from "../../entities/data-journal/api";
import { useFeatureEnabled } from "../../shared/features/FeatureProvider";
import { useNearViewport } from "../../shared/lib/useNearViewport";
import { ErrorState } from "../../shared/ui/ErrorState";
import { DataJournalEmptyState } from "./DataJournalEmptyState";
import { DataJournalEntryCard } from "./DataJournalEntryCard";

type CountryDataJournalBlockProps = {
  countrySlug: string;
  locale: LocaleCode;
};

export function CountryDataJournalBlock({
  countrySlug,
  locale,
}: CountryDataJournalBlockProps) {
  const sectionRef = useRef<HTMLDivElement>(null);
  const isNear = useNearViewport(sectionRef);
  const isEnabled = useFeatureEnabled("data_journal_enabled");

  const { data, error, isPending, isError } = useQuery({
    ...countryDataJournalQuery(countrySlug, locale),
    enabled: isNear && isEnabled,
  });

  if (!isEnabled) return null;

  if (!isNear || isPending) {
    return (
      <div ref={sectionRef}>
        <Skeleton lines={3} />
      </div>
    );
  }

  if (isError) {
    return (
      <div data-testid="data-journal-error">
        <ErrorState error={isApiError(error) ? error : undefined} />
      </div>
    );
  }

  const items = data?.items ?? [];

  if (items.length === 0) {
    return <DataJournalEmptyState />;
  }

  return (
    <div
      className="grid grid-cols-1 gap-4 md:grid-cols-2"
      data-testid="data-journal-block"
    >
      {items.map((entry) => (
        <DataJournalEntryCard
          key={entry.id}
          entry={entry}
        />
      ))}
    </div>
  );
}
