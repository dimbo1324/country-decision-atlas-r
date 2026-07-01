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

const DRIFT_VARIANT: Record<string, string> = {
  positive: "badge--trust",
  mildly_positive: "badge--info",
  stable: "badge--default",
  negative: "badge--warning",
  insufficient_data: "badge--default",
};

const DRIFT_LABELS: Record<string, string> = {
  positive: "Направление: улучшается",
  mildly_positive: "Направление: умеренно улучшается",
  stable: "Направление: стабильно",
  negative: "Направление: ухудшается",
  insufficient_data: "Недостаточно данных",
};

export function CountryDriftBadge({ label }: CountryDriftBadgeProps) {
  const cls = DRIFT_VARIANT[label] ?? "badge--default";
  const text = DRIFT_LABELS[label] ?? label;
  return (
    <span
      className={`badge ${cls}`}
      title="Индикатор тренда на основе правовых сигналов"
    >
      {text}
    </span>
  );
}
