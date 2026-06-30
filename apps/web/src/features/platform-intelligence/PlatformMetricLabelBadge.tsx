type LabelBadgeProps = {
  label: string;
};

export function PlatformMetricLabelBadge({ label }: LabelBadgeProps) {
  return (
    <span className="platformMetricLabel" data-label={label}>
      {label}
    </span>
  );
}
