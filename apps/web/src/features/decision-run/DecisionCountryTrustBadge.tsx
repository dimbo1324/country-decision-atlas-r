"use client";

import { useEffect, useState } from "react";

import type { CountryTrustResponse } from "../../shared/api/trust";
import { getCountryTrust } from "../../shared/api/trust";
import { FreshnessBadge } from "../../shared/ui/FreshnessBadge";
import { TrustBadge } from "../../shared/ui/TrustBadge";

type DecisionCountryTrustBadgeProps = {
  countrySlug: string;
  locale: string;
};

export function DecisionCountryTrustBadge({
  countrySlug,
  locale,
}: DecisionCountryTrustBadgeProps) {
  const [trust, setTrust] = useState<CountryTrustResponse | null>(null);

  useEffect(() => {
    let mounted = true;
    getCountryTrust(
      countrySlug,
      locale as Parameters<typeof getCountryTrust>[1],
    )
      .then((r) => {
        if (mounted) setTrust(r);
      })
      .catch(() => {});
    return () => {
      mounted = false;
    };
  }, [countrySlug, locale]);

  if (!trust) return null;

  return (
    <div
      className="decisionTrustContext"
      data-testid="decision-trust-context"
    >
      <span className="trustContextLabel">Качество данных:</span>
      <TrustBadge
        label={trust.trust_label}
        score={trust.trust_score ?? undefined}
      />
      <FreshnessBadge status={trust.freshness_status} />
    </div>
  );
}
