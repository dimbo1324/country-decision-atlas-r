"use client";

import { useEffect, useState } from "react";

import type { LocaleCode } from "../../shared/api/countries";
import { isApiError } from "../../shared/api/http";
import type { WhatChangedResponse } from "../../shared/api/what-changed";
import { whatChangedApi } from "../../shared/api/what-changed";
import { ErrorState } from "../../shared/ui/ErrorState";
import { WhatChangedItemCard } from "./WhatChangedItemCard";

type CountryWhatChangedProps = {
  countrySlug: string;
  locale: LocaleCode;
};

const DISPLAY_LIMIT = 5;

export function CountryWhatChanged({
  countrySlug,
  locale,
}: CountryWhatChangedProps) {
  const [data, setData] = useState<WhatChangedResponse | null>(null);
  const [error, setError] = useState<unknown | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    setIsLoading(true);
    setError(null);
    whatChangedApi
      .getCountryWhatChanged(countrySlug, {
        locale,
        days: 30,
        limit: DISPLAY_LIMIT,
      })
      .then((response) => {
        if (isMounted) {
          setData(response);
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
    return <div className="notice">Загрузка изменений…</div>;
  }

  if (error !== null) {
    return (
      <div data-testid="what-changed-error">
        <ErrorState error={isApiError(error) ? error : undefined} />
      </div>
    );
  }

  const items = data?.items ?? [];

  if (items.length === 0) {
    return (
      <div
        className="notice"
        data-testid="what-changed-empty"
      >
        Пока нет изменений за выбранный период.
      </div>
    );
  }

  return (
    <div data-testid="what-changed-block">
      {data && (
        <p className="formHint">
          С {new Date(data.since).toLocaleDateString("ru-RU")} · всего
          изменений: {data.summary.total}
        </p>
      )}
      <div className="sourceGrid">
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
