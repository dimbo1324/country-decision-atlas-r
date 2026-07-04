"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import {
  isApiError,
  type CountryTrustResponse,
  type LocaleCode,
} from "../../shared/api";
import { getCountryTrust } from "../../shared/api/trust";
import { ConfidenceBadge } from "../../shared/ui/ConfidenceBadge";
import { DisclaimerNotice } from "../../shared/ui/DisclaimerNotice";
import { ErrorState } from "../../shared/ui/ErrorState";
import { FreshnessBadge } from "../../shared/ui/FreshnessBadge";
import { LastVerifiedAt } from "../../shared/ui/LastVerifiedAt";
import { TrustBadge } from "../../shared/ui/TrustBadge";

type TrustSurfaceBlockProps = {
  countrySlug: string;
  locale: LocaleCode;
};

export function TrustSurfaceBlock({
  countrySlug,
  locale,
}: TrustSurfaceBlockProps) {
  const [data, setData] = useState<CountryTrustResponse | null>(null);
  const [error, setError] = useState<unknown | null>(null);
  const [isNotComputed, setIsNotComputed] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    setIsLoading(true);
    setError(null);
    setIsNotComputed(false);
    getCountryTrust(countrySlug, locale)
      .then((res) => {
        if (isMounted) {
          setData(res);
        }
      })
      .catch((err: unknown) => {
        if (isMounted) {
          setData(null);
          if (isApiError(err) && err.error?.code === "trust_not_found") {
            setIsNotComputed(true);
          } else {
            setError(err);
          }
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
    return <div className="notice">Загрузка индикатора доверия...</div>;
  }

  if (error !== null) {
    return (
      <div data-testid="trust-surface-error">
        <ErrorState error={isApiError(error) ? error : undefined} />
      </div>
    );
  }

  if (!data || isNotComputed) {
    return (
      <div
        className="notice"
        data-testid="trust-surface-empty"
      >
        Данные о доверии к источникам ещё не вычислены для этой страны.
      </div>
    );
  }

  const contradictionLabel = (() => {
    const score = data.components?.contradiction_component;
    if (score === null || score === undefined) return "Неизвестно";
    const raw = 100 - score;
    if (raw < 30) return "Низкая";
    if (raw < 60) return "Средняя";
    return "Высокая";
  })();

  return (
    <div data-testid="trust-surface-block">
      <div className="trustBadgeRow">
        <TrustBadge
          label={data.trust_label}
          score={data.trust_score ?? undefined}
        />
        <FreshnessBadge status={data.freshness_status} />
        {data.confidence && <ConfidenceBadge confidence={data.confidence} />}
      </div>
      <LastVerifiedAt date={data.last_verified_at ?? undefined} />
      <p
        className="infoNote"
        data-testid="contradiction-context"
      >
        Противоречивость данных:{" "}
        <span className="metaChip">{contradictionLabel}</span>
      </p>
      <p className="infoNote">
        <Link
          href="/methodology"
          className="internalLink"
        >
          О методологии →
        </Link>
      </p>
      <DisclaimerNotice text={data.disclaimer} />
    </div>
  );
}
