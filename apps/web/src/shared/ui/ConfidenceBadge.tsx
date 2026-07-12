import { Badge, type BadgeVariant } from "@country-decision-atlas/ui";

type Confidence = "low" | "medium" | "high" | string;

type ConfidenceBadgeProps = {
  confidence: Confidence;
};

const CONFIDENCE_VARIANT: Record<string, BadgeVariant> = {
  high: "trust",
  medium: "info",
  low: "warning",
};

const CONFIDENCE_LABELS: Record<string, string> = {
  high: "высокая",
  medium: "средняя",
  low: "низкая",
};

export function ConfidenceBadge({ confidence }: ConfidenceBadgeProps) {
  const variant = CONFIDENCE_VARIANT[confidence] ?? "default";
  const label = CONFIDENCE_LABELS[confidence] ?? confidence;
  return <Badge variant={variant}>Достоверность: {label}</Badge>;
}
