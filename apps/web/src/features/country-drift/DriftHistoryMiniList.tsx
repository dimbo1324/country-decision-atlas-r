import { Badge } from "@country-decision-atlas/ui";
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
    <ul
      className="flex flex-col gap-2"
      data-testid="drift-history-mini-list"
    >
      {items.map((item) => (
        <li
          key={`${item.period_start}-${item.period_end}`}
          className="flex items-center justify-between gap-3"
        >
          <Badge variant="default">
            {item.period_start} — {item.period_end}
          </Badge>
          <CountryDriftBadge label={item.label} />
        </li>
      ))}
    </ul>
  );
}
