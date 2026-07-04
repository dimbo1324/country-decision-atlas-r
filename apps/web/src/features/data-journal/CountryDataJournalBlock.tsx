"use client";

import { useEffect, useState } from "react";

import { isApiError } from "../../shared/api";
import { getCountryDataJournal } from "../../shared/api/data-journal";
import type { CountryDataJournalResponse } from "../../shared/api/data-journal";
import type { LocaleCode } from "../../shared/api/countries";
import { getFeatures } from "../../shared/api/feature-flags";
import { isFeatureEnabled } from "../../shared/lib/features";
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
  const [data, setData] = useState<CountryDataJournalResponse | null>(null);
  const [error, setError] = useState<unknown | null>(null);
  const [isEnabled, setIsEnabled] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    setIsLoading(true);
    setError(null);
    Promise.all([
      getFeatures("public"),
      getCountryDataJournal(countrySlug, locale, 10, 0),
    ])
      .then(([features, journal]) => {
        if (isMounted) {
          setIsEnabled(isFeatureEnabled(features, "data_journal_enabled"));
          setData(journal);
        }
      })
      .catch((err: unknown) => {
        if (isMounted) {
          setData(null);
          setError(err);
        }
      })
      .finally(() => {
        if (isMounted) {
          setIsLoading(false);
        }
      });
    return () => {
      isMounted = false;
    };
  }, [countrySlug, locale]);

  if (isLoading) {
    return <div className="notice">Загрузка обновлений данных...</div>;
  }

  if (error !== null) {
    return (
      <div data-testid="data-journal-error">
        <ErrorState error={isApiError(error) ? error : undefined} />
      </div>
    );
  }

  if (!isEnabled) {
    return null;
  }

  const items = data?.items ?? [];

  if (items.length === 0) {
    return <DataJournalEmptyState />;
  }

  return (
    <div
      className="sourceGrid"
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
