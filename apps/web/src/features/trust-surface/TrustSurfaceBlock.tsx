"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import type { CountryTrustResponse, LocaleCode } from "../../shared/api";
import { getCountryTrust } from "../../shared/api/trust";
import { ConfidenceBadge } from "../../shared/ui/ConfidenceBadge";
import { DisclaimerNotice } from "../../shared/ui/DisclaimerNotice";
import { FreshnessBadge } from "../../shared/ui/FreshnessBadge";
import { LastVerifiedAt } from "../../shared/ui/LastVerifiedAt";
import { TrustBadge } from "../../shared/ui/TrustBadge";

type TrustSurfaceBlockProps = {
  countrySlug: string;
  locale: LocaleCode;
};

export function TrustSurfaceBlock({ countrySlug, locale }: TrustSurfaceBlockProps) {
  const [data, setData] = useState<CountryTrustResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    setIsLoading(true);
    getCountryTrust(countrySlug, locale)
      .then((res) => {
        if (isMounted) setData(res);
      })
      .catch(() => {
        if (isMounted) setData(null);
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

  if (!data) {
    return (
      <div className="notice" data-testid="trust-surface-empty">
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
        <TrustBadge label={data.trust_label} score={data.trust_score ?? undefined} />
        <FreshnessBadge status={data.freshness_status} />
        {data.confidence && <ConfidenceBadge confidence={data.confidence} />}
      </div>
      <LastVerifiedAt date={data.last_verified_at ?? undefined} />
      <p className="infoNote" data-testid="contradiction-context">
        Противоречивость данных: <span className="metaChip">{contradictionLabel}</span>
      </p>
      <p className="infoNote">
        <Link href="/methodology" className="internalLink">
          О методологии →
        </Link>
      </p>
      <DisclaimerNotice text={data.disclaimer} />
    </div>
  );
}
