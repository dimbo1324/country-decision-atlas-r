"use client";

import { useQuery } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import { Skeleton } from "@country-decision-atlas/ui";
import { isApiError, type LocaleCode } from "../../shared/api";
import { countryDriftQuery } from "../../entities/country-drift/api";
import { ConfidenceBadge } from "../../shared/ui/ConfidenceBadge";
import { DisclaimerNotice } from "../../shared/ui/DisclaimerNotice";
import { ErrorState } from "../../shared/ui/ErrorState";
import { CountryDriftBadge } from "./CountryDriftBadge";
import { DriftHistoryMiniList } from "./DriftHistoryMiniList";
import { formatDateTime } from "../../shared/lib/format";
import { useAppLocale } from "../../shared/lib/useAppLocale";

type CountryDriftBlockProps = {
  countrySlug: string;
  locale: LocaleCode;
};

export function CountryDriftBlock({
  countrySlug,
  locale,
}: CountryDriftBlockProps) {
  const t = useTranslations("countryDrift");
  const uiLocale = useAppLocale();
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
        {t("empty")}
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
        {t("eventsInPeriod", { count: snapshot.event_count })} ·{" "}
        {t("windowDays", { days: snapshot.window_days })}
        {snapshot.net_score != null && (
          <> · {t("netScore", { value: snapshot.net_score.toFixed(1) })}</>
        )}
      </p>
      <p
        className="text-c4 text-xs"
        data-testid="country-drift-computed-at"
      >
        {t("computedAt", {
          date: formatDateTime(snapshot.computed_at, uiLocale),
        })}
      </p>
      <p className="text-c4 text-xs">{t("disclaimer")}</p>
      <DriftHistoryMiniList items={data?.history ?? []} />
      <DisclaimerNotice text={data?.disclaimer} />
    </div>
  );
}
