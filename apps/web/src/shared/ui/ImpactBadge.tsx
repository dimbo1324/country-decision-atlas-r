import { Badge, type BadgeVariant } from "@country-decision-atlas/ui";

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

const DIRECTION_VARIANT: Record<string, BadgeVariant> = {
  positive: "positive",
  negative: "negative",
  mixed: "warning",
  neutral: "default",
  uncertain: "warning",
};

const LEVEL_VARIANT: Record<string, BadgeVariant> = {
  low: "info",
  medium: "warning",
  high: "negative",
  critical: "critical",
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
  const variant = DIRECTION_VARIANT[direction] ?? "default";
  const label = DIRECTION_LABELS[direction] ?? direction;
  return <Badge variant={variant}>{label}</Badge>;
}

export function ImpactLevelBadge({ level }: ImpactLevelBadgeProps) {
  const variant = LEVEL_VARIANT[level] ?? "default";
  const label = LEVEL_LABELS[level] ?? level;
  return <Badge variant={variant}>{label}</Badge>;
}
