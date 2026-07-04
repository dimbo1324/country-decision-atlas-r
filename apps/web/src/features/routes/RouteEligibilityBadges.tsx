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

const VALUE_CLASSES = {
  yes: "routeEligibilityYes",
  no: "routeEligibilityNo",
  unknown: "routeEligibilityUnknown",
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
    <div className="routeEligibility">
      {visibleEntries.map(([key, value]) => (
        <span
          key={key}
          className={`routeEligibilityBadge ${VALUE_CLASSES[value]}`}
        >
          <span>{LABELS[key]}</span>
          <strong>{VALUE_LABELS[value]}</strong>
        </span>
      ))}
    </div>
  );
}
