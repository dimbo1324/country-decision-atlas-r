import { Badge, type BadgeVariant } from "@country-decision-atlas/ui";

type FreshnessStatus = "fresh" | "aging" | "stale" | "unknown" | string;

type FreshnessBadgeProps = {
  status: FreshnessStatus;
};

const FRESHNESS_VARIANT: Record<string, BadgeVariant> = {
  fresh: "trust",
  aging: "info",
  stale: "warning",
  unknown: "default",
};

const FRESHNESS_LABELS: Record<string, string> = {
  fresh: "актуальные",
  aging: "устаревающие",
  stale: "устаревшие",
  unknown: "неизвестно",
};

export function FreshnessBadge({ status }: FreshnessBadgeProps) {
  const variant = FRESHNESS_VARIANT[status] ?? "default";
  const label = FRESHNESS_LABELS[status] ?? status;
  return <Badge variant={variant}>Данные: {label}</Badge>;
}
