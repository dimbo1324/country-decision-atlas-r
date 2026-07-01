"use client";

import { useEffect, useState } from "react";

import { isApiError, type LocaleCode } from "../../shared/api";
import {
  getCountryDrift,
  type CountryDriftResponse,
} from "../../shared/api/country-drift";
import { ConfidenceBadge } from "../../shared/ui/ConfidenceBadge";
import { DisclaimerNotice } from "../../shared/ui/DisclaimerNotice";
import { ErrorState } from "../../shared/ui/ErrorState";
import { CountryDriftBadge } from "./CountryDriftBadge";
import { DriftHistoryMiniList } from "./DriftHistoryMiniList";

type CountryDriftBlockProps = {
  countrySlug: string;
  locale: LocaleCode;
};

export function CountryDriftBlock({ countrySlug, locale }: CountryDriftBlockProps) {
  const [data, setData] = useState<CountryDriftResponse | null>(null);
  const [error, setError] = useState<unknown | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    setIsLoading(true);
    setError(null);
    getCountryDrift(countrySlug, locale)
      .then((res) => {
        if (isMounted) {
          setData(res);
        }
      })
      .catch((err: unknown) => {
        if (isMounted) {
          setData(null);
          setError(err);
        }
      })
      .finally(() => {
        if (isMounted) setIsLoading(false);
      });
    return () => {
      isMounted = false;
    };
  }, [countrySlug, locale]);

  if (isLoading) {
    return <div className="notice">Загрузка индикатора тренда...</div>;
  }

  if (error !== null) {
    return (
      <div data-testid="country-drift-error">
        <ErrorState error={isApiError(error) ? error : undefined} />
      </div>
    );
  }

  const snapshot = data?.latest_snapshot ?? null;

  if (!snapshot) {
    return (
      <div className="notice" data-testid="country-drift-empty">
        Данные о направлении изменений ещё не вычислены для этой страны.
      </div>
    );
  }

  return (
    <div data-testid="country-drift-block">
      <div className="trustBadgeRow">
        <CountryDriftBadge label={snapshot.label} />
        <ConfidenceBadge confidence={snapshot.confidence} />
      </div>
      <p className="infoNote" data-testid="country-drift-metrics">
        Событий за период: {snapshot.event_count} · Окно: {snapshot.window_days} дней
        {snapshot.net_score != null && (
          <> · Net score: {snapshot.net_score.toFixed(1)}</>
        )}
      </p>
      <p className="infoNote" data-testid="country-drift-computed-at">
        Рассчитано: {new Date(snapshot.computed_at).toLocaleString("ru")}
      </p>
      <p className="infoNote">
        Индикатор основан только на официальных правовых сигналах за выбранный период и
        не является прогнозом.
      </p>
      <DriftHistoryMiniList items={data?.history ?? []} />
      <DisclaimerNotice text={data?.disclaimer} />
    </div>
  );
}
