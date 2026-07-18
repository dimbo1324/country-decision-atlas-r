import { Badge, type BadgeVariant } from "@country-decision-atlas/ui";
import type { SupportedLocale } from "../lib/locale";
import { useAppLocale } from "../lib/useAppLocale";

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

const DIRECTION_LABELS: Record<SupportedLocale, Record<string, string>> = {
  en: {
    positive: "positive",
    negative: "negative",
    mixed: "mixed",
    neutral: "neutral",
    uncertain: "uncertain",
  },
  ru: {
    positive: "положительное",
    negative: "отрицательное",
    mixed: "смешанное",
    neutral: "нейтральное",
    uncertain: "неопределённое",
  },
  es: {
    positive: "positivo",
    negative: "negativo",
    mixed: "mixto",
    neutral: "neutral",
    uncertain: "incierto",
  },
};

const LEVEL_LABELS: Record<SupportedLocale, Record<string, string>> = {
  en: {
    low: "low",
    medium: "medium",
    high: "high",
    critical: "critical",
  },
  ru: {
    low: "низкий",
    medium: "средний",
    high: "высокий",
    critical: "критический",
  },
  es: {
    low: "bajo",
    medium: "medio",
    high: "alto",
    critical: "crítico",
  },
};

export function ImpactDirectionBadge({ direction }: ImpactDirectionBadgeProps) {
  const locale = useAppLocale();
  const variant = DIRECTION_VARIANT[direction] ?? "default";
  const label = DIRECTION_LABELS[locale][direction] ?? direction;
  return <Badge variant={variant}>{label}</Badge>;
}

export function ImpactLevelBadge({ level }: ImpactLevelBadgeProps) {
  const locale = useAppLocale();
  const variant = LEVEL_VARIANT[level] ?? "default";
  const label = LEVEL_LABELS[locale][level] ?? level;
  return <Badge variant={variant}>{label}</Badge>;
}
