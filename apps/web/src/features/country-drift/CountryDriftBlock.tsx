"use client";

import { useQuery } from "@tanstack/react-query";
import { Skeleton } from "@country-decision-atlas/ui";
import { isApiError, type LocaleCode } from "../../shared/api";
import { countryDriftQuery } from "../../entities/country-drift/api";
import { ConfidenceBadge } from "../../shared/ui/ConfidenceBadge";
import { DisclaimerNotice } from "../../shared/ui/DisclaimerNotice";
import { ErrorState } from "../../shared/ui/ErrorState";
import { CountryDriftBadge } from "./CountryDriftBadge";
import { DriftHistoryMiniList } from "./DriftHistoryMiniList";

type CountryDriftBlockProps = {
  countrySlug: string;
  locale: LocaleCode;
};

export function CountryDriftBlock({
  countrySlug,
  locale,
}: CountryDriftBlockProps) {
  const { data, error, isPending, isError } = useQuery(
    countryDriftQuery(countrySlug, locale),
  );

  if (isPending) {
    return <Skeleton lines={3} />;
  }

  if (isError) {
    return (
      <div data-testid="country-drift-error">
        <ErrorState error={isApiError(error) ? error : undefined} />
      </div>
    );
  }

  const snapshot = data?.latest_snapshot ?? null;

  if (!snapshot) {
    return (
      <p
        className="text-c4 text-sm"
        data-testid="country-drift-empty"
      >
        Данные о направлении изменений ещё не вычислены для этой страны.
      </p>
    );
  }

  return (
    <div
      className="flex flex-col gap-4"
      data-testid="country-drift-block"
    >
      <div className="flex flex-wrap items-center gap-2">
        <CountryDriftBadge label={snapshot.label} />
        <ConfidenceBadge confidence={snapshot.confidence} />
      </div>
      <p
        className="text-c3 text-sm"
        data-testid="country-drift-metrics"
      >
        Событий за период: {snapshot.event_count} · Окно: {snapshot.window_days}{" "}
        дней
        {snapshot.net_score != null && (
          <> · Net score: {snapshot.net_score.toFixed(1)}</>
        )}
      </p>
      <p
        className="text-c4 text-xs"
        data-testid="country-drift-computed-at"
      >
        Рассчитано: {new Date(snapshot.computed_at).toLocaleString("ru")}
      </p>
      <p className="text-c4 text-xs">
        Индикатор основан только на официальных правовых сигналах за выбранный
        период и не является прогнозом.
      </p>
      <DriftHistoryMiniList items={data?.history ?? []} />
      <DisclaimerNotice text={data?.disclaimer} />
    </div>
  );
}
