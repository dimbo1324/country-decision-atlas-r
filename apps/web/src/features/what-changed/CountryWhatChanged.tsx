"use client";

import { useQuery } from "@tanstack/react-query";
import { Kicker, Skeleton } from "@country-decision-atlas/ui";
import type { LocaleCode } from "../../shared/api/countries";
import { isApiError } from "../../shared/api/http";
import { countryWhatChangedQuery } from "../../entities/what-changed/api";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ErrorState } from "../../shared/ui/ErrorState";
import { WhatChangedItemCard } from "./WhatChangedItemCard";

type CountryWhatChangedProps = {
  countrySlug: string;
  locale: LocaleCode;
};

export function CountryWhatChanged({
  countrySlug,
  locale,
}: CountryWhatChangedProps) {
  const { data, error, isPending, isError } = useQuery(
    countryWhatChangedQuery(countrySlug, locale),
  );

  if (isPending) {
    return <Skeleton lines={3} />;
  }

  if (isError) {
    return (
      <div data-testid="what-changed-error">
        <ErrorState error={isApiError(error) ? error : undefined} />
      </div>
    );
  }

  const items = data?.items ?? [];

  if (items.length === 0) {
    return (
      <div data-testid="what-changed-empty">
        <EmptyState message="Пока нет изменений за выбранный период." />
      </div>
    );
  }

  return (
    <div
      className="flex flex-col gap-4"
      data-testid="what-changed-block"
    >
      {data && (
        <Kicker>
          С {new Date(data.since).toLocaleDateString("ru-RU")} · всего
          изменений: {data.summary.total}
        </Kicker>
      )}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {items.map((item) => (
          <WhatChangedItemCard
            key={item.id}
            item={item}
          />
        ))}
      </div>
    </div>
  );
}
