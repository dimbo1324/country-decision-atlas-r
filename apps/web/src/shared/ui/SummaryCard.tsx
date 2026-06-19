type SummaryCardProps = {
  label: string;
  value: string | number;
  detail?: string;
};

export function SummaryCard({ label, value, detail }: SummaryCardProps) {
  return (
    <div className="summaryCard">
      <span className="summaryLabel">{label}</span>
      <strong className="summaryValue">{value}</strong>
      {detail && <span className="summaryDetail">{detail}</span>}
    </div>
  );
}
