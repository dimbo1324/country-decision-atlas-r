"use client";

import { useEffect, useState } from "react";

import { getCountryDataJournal } from "../../shared/api/data-journal";
import type { CountryDataJournalResponse } from "../../shared/api/data-journal";
import type { LocaleCode } from "../../shared/api/countries";
import { getFeatures } from "../../shared/api/feature-flags";
import { isFeatureEnabled } from "../../shared/lib/features";
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
  const [isEnabled, setIsEnabled] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    setIsLoading(true);
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
      .catch(() => {
        if (isMounted) {
          setIsEnabled(false);
          setData(null);
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

  if (!isEnabled) {
    return null;
  }

  const items = data?.items ?? [];

  if (items.length === 0) {
    return <DataJournalEmptyState />;
  }

  return (
    <div className="sourceGrid" data-testid="data-journal-block">
      {items.map((entry) => (
        <DataJournalEntryCard key={entry.id} entry={entry} />
      ))}
    </div>
  );
}
