type Confidence = "low" | "medium" | "high" | string;

type ConfidenceBadgeProps = {
  confidence: Confidence;
};

const CONFIDENCE_VARIANT: Record<string, string> = {
  high: "badge--trust",
  medium: "badge--info",
  low: "badge--warning",
};

const CONFIDENCE_LABELS: Record<string, string> = {
  high: "высокая",
  medium: "средняя",
  low: "низкая",
};

export function ConfidenceBadge({ confidence }: ConfidenceBadgeProps) {
  const cls = CONFIDENCE_VARIANT[confidence] ?? "badge--default";
  const label = CONFIDENCE_LABELS[confidence] ?? confidence;
  return <span className={`badge ${cls}`}>Достоверность: {label}</span>;
}
