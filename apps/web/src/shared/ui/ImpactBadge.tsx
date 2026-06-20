type ImpactDirection =
  | "positive"
  | "negative"
  | "mixed"
  | "neutral"
  | "uncertain"
  | string;
type ImpactLevel = "low" | "medium" | "high" | "critical" | string;

type ImpactDirectionBadgeProps = {
  direction: ImpactDirection;
};

type ImpactLevelBadgeProps = {
  level: ImpactLevel;
};

const DIRECTION_VARIANT: Record<string, string> = {
  positive: "badge--positive",
  negative: "badge--negative",
  mixed: "badge--warning",
  neutral: "badge--default",
  uncertain: "badge--warning",
};

const LEVEL_VARIANT: Record<string, string> = {
  low: "badge--info",
  medium: "badge--warning",
  high: "badge--negative",
  critical: "badge--critical",
};

const DIRECTION_LABELS: Record<string, string> = {
  positive: "положительное",
  negative: "отрицательное",
  mixed: "смешанное",
  neutral: "нейтральное",
  uncertain: "неопределённое",
};

const LEVEL_LABELS: Record<string, string> = {
  low: "низкий",
  medium: "средний",
  high: "высокий",
  critical: "критический",
};

export function ImpactDirectionBadge({ direction }: ImpactDirectionBadgeProps) {
  const cls = DIRECTION_VARIANT[direction] ?? "badge--default";
  const label = DIRECTION_LABELS[direction] ?? direction;
  return <span className={`badge ${cls}`}>{label}</span>;
}

export function ImpactLevelBadge({ level }: ImpactLevelBadgeProps) {
  const cls = LEVEL_VARIANT[level] ?? "badge--default";
  const label = LEVEL_LABELS[level] ?? level;
  return <span className={`badge ${cls}`}>{label}</span>;
}
