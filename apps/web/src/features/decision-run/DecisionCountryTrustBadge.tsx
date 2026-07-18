"use client";

import { useQuery } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import type { components } from "@country-decision-atlas/contracts/generated/types";
import { countryTrustQuery } from "../../entities/trust-surface/api";
import { FreshnessBadge } from "../../shared/ui/FreshnessBadge";
import { TrustBadge } from "../../shared/ui/TrustBadge";

type LocaleCode = components["schemas"]["LocaleCode"];

type DecisionCountryTrustBadgeProps = {
  countrySlug: string;
  locale: string;
};

export function DecisionCountryTrustBadge({
  countrySlug,
  locale,
}: DecisionCountryTrustBadgeProps) {
  const t = useTranslations("decisionRun");
  const { data: trust } = useQuery(
    countryTrustQuery(countrySlug, locale as LocaleCode),
  );

  if (!trust) return null;

  return (
    <div
      className="flex items-center gap-2"
      data-testid="decision-trust-context"
    >
      <span className="text-c4 text-xs">{t("dataQuality")}</span>
      <TrustBadge
        label={trust.trust_label}
        score={trust.trust_score ?? undefined}
      />
      <FreshnessBadge status={trust.freshness_status} />
    </div>
  );
}
