import { Badge } from "./Badge";

type BadgeVariant = "default" | "positive" | "negative" | "warning" | "critical" | "info";

const STATUS_VARIANTS: Record<string, BadgeVariant> = {
  published: "positive",
  valid: "positive",
  passed: "positive",
  draft: "warning",
  review: "info",
  warning: "warning",
  invalid: "critical",
  failed: "critical",
  archived: "default",
};

type StatusBadgeProps = {
  status: string;
};

export function StatusBadge({ status }: StatusBadgeProps) {
  return (
    <Badge variant={STATUS_VARIANTS[status] ?? "default"}>{status}</Badge>
  );
}
