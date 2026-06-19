type Confidence = "low" | "medium" | "high" | string;

type ConfidenceBadgeProps = {
  confidence: Confidence;
};

const CONFIDENCE_VARIANT: Record<string, string> = {
  high: "badge--trust",
  medium: "badge--info",
  low: "badge--warning",
};

export function ConfidenceBadge({ confidence }: ConfidenceBadgeProps) {
  const cls = CONFIDENCE_VARIANT[confidence] ?? "badge--default";
  return <span className={`badge ${cls}`}>Confidence: {confidence}</span>;
}
