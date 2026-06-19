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

export function ImpactDirectionBadge({ direction }: ImpactDirectionBadgeProps) {
  const cls = DIRECTION_VARIANT[direction] ?? "badge--default";
  return <span className={`badge ${cls}`}>{direction}</span>;
}

export function ImpactLevelBadge({ level }: ImpactLevelBadgeProps) {
  const cls = LEVEL_VARIANT[level] ?? "badge--default";
  return <span className={`badge ${cls}`}>{level}</span>;
}
