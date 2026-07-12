import { Badge, type BadgeVariant } from "@country-decision-atlas/ui";

type TrustLabel =
  | "very_high"
  | "high"
  | "medium"
  | "low"
  | "very_low"
  | "insufficient_data"
  | string;

type TrustBadgeProps = {
  label: TrustLabel;
  score?: number | null;
};

const TRUST_VARIANT: Record<string, BadgeVariant> = {
  very_high: "trust",
  high: "trust",
  medium: "info",
  low: "warning",
  very_low: "warning",
  insufficient_data: "default",
};

const TRUST_LABELS: Record<string, string> = {
  very_high: "Очень высокое",
  high: "Высокое",
  medium: "Среднее",
  low: "Низкое",
  very_low: "Очень низкое",
  insufficient_data: "Недостаточно данных",
};

export function TrustBadge({ label, score }: TrustBadgeProps) {
  const variant = TRUST_VARIANT[label] ?? "default";
  const text = TRUST_LABELS[label] ?? label;
  return (
    <Badge
      variant={variant}
      title="Индикатор качества данных"
    >
      Доверие: {text}
      {score != null && ` (${score.toFixed(0)})`}
    </Badge>
  );
}
