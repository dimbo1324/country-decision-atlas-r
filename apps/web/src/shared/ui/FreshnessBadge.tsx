type FreshnessStatus = "fresh" | "aging" | "stale" | "unknown" | string;

type FreshnessBadgeProps = {
  status: FreshnessStatus;
};

const FRESHNESS_VARIANT: Record<string, string> = {
  fresh: "badge--trust",
  aging: "badge--info",
  stale: "badge--warning",
  unknown: "badge--default",
};

const FRESHNESS_LABELS: Record<string, string> = {
  fresh: "актуальные",
  aging: "устаревающие",
  stale: "устаревшие",
  unknown: "неизвестно",
};

export function FreshnessBadge({ status }: FreshnessBadgeProps) {
  const cls = FRESHNESS_VARIANT[status] ?? "badge--default";
  const label = FRESHNESS_LABELS[status] ?? status;
  return <span className={`badge ${cls}`}>Данные: {label}</span>;
}
