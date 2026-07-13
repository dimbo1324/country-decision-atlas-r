import { Badge, type BadgeVariant } from "@country-decision-atlas/ui";

type LabelBadgeProps = {
  label: string;
};

const LABEL_VARIANT: Record<string, BadgeVariant> = {
  insufficient_data: "default",
  low: "trust",
  moderate: "warning",
  elevated: "warning",
  high: "critical",
};

export function PlatformMetricLabelBadge({ label }: LabelBadgeProps) {
  return (
    <Badge
      variant={LABEL_VARIANT[label] ?? "default"}
      title={label}
    >
      {label}
    </Badge>
  );
}
