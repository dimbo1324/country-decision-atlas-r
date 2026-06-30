"use client";

import { useEffect, useState } from "react";

import type { CountryTrustResponse, LocaleCode } from "../../shared/api";
import { getCountryTrust } from "../../shared/api/trust";
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

  return (
    <div data-testid="trust-surface-block">
      <div className="trustBadgeRow">
        <TrustBadge label={data.trust_label} score={data.trust_score ?? undefined} />
        <FreshnessBadge status={data.freshness_status} />
        {data.confidence && (
          <span className="badge badge--default">
            Уверенность: {data.confidence === "high" ? "высокая" : data.confidence === "medium" ? "средняя" : "низкая"}
          </span>
        )}
      </div>
      <LastVerifiedAt date={data.last_verified_at ?? undefined} />
      <DisclaimerNotice text={data.disclaimer} />
    </div>
  );
}
