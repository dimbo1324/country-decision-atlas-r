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

/** Lowercase Russian confidence level, for reuse outside the badge. */
export function confidenceLabelRu(confidence: string): string {
  return CONFIDENCE_LABELS[confidence] ?? confidence;
}

export function ConfidenceBadge({ confidence }: ConfidenceBadgeProps) {
  const variant = CONFIDENCE_VARIANT[confidence] ?? "default";
  const label = CONFIDENCE_LABELS[confidence] ?? confidence;
  return <Badge variant={variant}>Достоверность: {label}</Badge>;
}
