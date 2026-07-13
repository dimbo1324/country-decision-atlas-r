import { Badge, type BadgeVariant } from "@country-decision-atlas/ui";
import type { RouteEligibility } from "../../shared/api/routes";

const LABELS: Record<keyof RouteEligibility, string> = {
  allows_work: "Можно работать",
  allows_family: "Можно с семьёй",
  leads_to_pr: "Ведёт к ПМЖ",
  leads_to_citizenship: "Ведёт к гражданству",
  requires_income_proof: "Нужен доход",
  requires_local_address: "Нужен адрес",
  requires_criminal_record_check: "Нужна справка о несудимости",
};

const VALUE_LABELS = {
  yes: "Да",
  no: "Нет",
  unknown: "Неизвестно",
};

const VALUE_VARIANT: Record<keyof typeof VALUE_LABELS, BadgeVariant> = {
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
            {LABELS[key]}: {VALUE_LABELS[value]}
          </Badge>
        </span>
      ))}
    </div>
  );
}
