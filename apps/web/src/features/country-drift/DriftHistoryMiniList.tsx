import type { CountryDriftHistoryItem } from "../../shared/api/country-drift";
import { CountryDriftBadge } from "./CountryDriftBadge";

type DriftHistoryMiniListProps = {
  items: CountryDriftHistoryItem[];
};

export function DriftHistoryMiniList({ items }: DriftHistoryMiniListProps) {
  if (items.length === 0) {
    return null;
  }
  return (
    <ul className="driftHistoryMiniList" data-testid="drift-history-mini-list">
      {items.map((item) => (
        <li key={`${item.period_start}-${item.period_end}`} className="driftHistoryRow">
          <span className="metaChip">
            {item.period_start} — {item.period_end}
          </span>
          <CountryDriftBadge label={item.label} />
        </li>
      ))}
    </ul>
  );
}
