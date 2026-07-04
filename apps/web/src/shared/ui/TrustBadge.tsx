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

const TRUST_VARIANT: Record<string, string> = {
  very_high: "badge--trust",
  high: "badge--trust",
  medium: "badge--info",
  low: "badge--warning",
  very_low: "badge--warning",
  insufficient_data: "badge--default",
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
  const cls = TRUST_VARIANT[label] ?? "badge--default";
  const text = TRUST_LABELS[label] ?? label;
  return (
    <span
      className={`badge ${cls}`}
      title="Индикатор качества данных"
    >
      Доверие: {text}
      {score != null && ` (${score.toFixed(0)})`}
    </span>
  );
}
