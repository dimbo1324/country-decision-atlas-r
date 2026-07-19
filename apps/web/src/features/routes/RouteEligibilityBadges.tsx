import { useTranslations } from "next-intl";
import { Badge, type BadgeVariant } from "@country-decision-atlas/ui";
import type { RouteEligibility } from "../../shared/api/routes";

const LABEL_KEYS: Record<keyof RouteEligibility, string> = {
  allows_work: "allowsWork",
  allows_family: "allowsFamily",
  leads_to_pr: "leadsToPr",
  leads_to_citizenship: "leadsToCitizenship",
  requires_income_proof: "requiresIncomeProof",
  requires_local_address: "requiresLocalAddress",
  requires_criminal_record_check: "requiresCriminalRecordCheck",
};

const VALUE_LABEL_KEYS = {
  yes: "yes",
  no: "no",
  unknown: "unknown",
} as const;

const VALUE_VARIANT: Record<keyof typeof VALUE_LABEL_KEYS, BadgeVariant> = {
  yes: "trust",
  no: "negative",
  unknown: "default",
};

export function RouteEligibilityBadges({
  eligibility,
  compact = false,
}: {
  eligibility: RouteEligibility;
  compact?: boolean;
}) {
  const t = useTranslations("routeDetail");
  const entries = Object.entries(eligibility) as [
    keyof RouteEligibility,
    RouteEligibility[keyof RouteEligibility],
  ][];
  const visibleEntries = compact ? entries.slice(0, 4) : entries;

  return (
    <div
      className="flex flex-wrap gap-2"
      data-testid="route-eligibility"
    >
      {visibleEntries.map(([key, value]) => (
        <span
          key={key}
          data-testid="route-eligibility-badge"
        >
          <Badge variant={VALUE_VARIANT[value]}>
            {t(LABEL_KEYS[key])}: {t(VALUE_LABEL_KEYS[value])}
          </Badge>
        </span>
      ))}
    </div>
  );
}
