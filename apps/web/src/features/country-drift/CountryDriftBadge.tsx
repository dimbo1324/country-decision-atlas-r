import { Badge, type BadgeVariant } from "@country-decision-atlas/ui";

type DriftLabel =
  | "insufficient_data"
  | "negative"
  | "stable"
  | "mildly_positive"
  | "positive"
  | string;

type CountryDriftBadgeProps = {
  label: DriftLabel;
};

const DRIFT_VARIANT: Record<string, BadgeVariant> = {
  positive: "trust",
  mildly_positive: "info",
  stable: "default",
  negative: "warning",
  insufficient_data: "default",
};

const DRIFT_LABELS: Record<string, string> = {
  positive: "Направление: улучшается",
  mildly_positive: "Направление: умеренно улучшается",
  stable: "Направление: стабильно",
  negative: "Направление: ухудшается",
  insufficient_data: "Недостаточно данных",
};

export function CountryDriftBadge({ label }: CountryDriftBadgeProps) {
  return (
    <Badge
      variant={DRIFT_VARIANT[label] ?? "default"}
      title="Индикатор тренда на основе правовых сигналов"
    >
      {DRIFT_LABELS[label] ?? label}
    </Badge>
  );
}
