import Link from "next/link";
import { Badge, Card } from "@country-decision-atlas/ui";
import type { WhatChangedItem } from "../../shared/api/what-changed";
import { ArrowNext } from "../../shared/ui/LinkArrow";
import { formatDate } from "../../shared/lib/format";
import { useAppLocale } from "../../shared/lib/useAppLocale";

type WhatChangedItemCardProps = {
  item: WhatChangedItem;
};

const IMPORTANCE_LABELS: Record<string, string> = {
  low: "Низкая",
  medium: "Средняя",
  high: "Высокая",
  critical: "Критичная",
};

export function WhatChangedItemCard({ item }: WhatChangedItemCardProps) {
  const locale = useAppLocale();
  const occurredAt = formatDate(item.occurred_at, locale);

  return (
    <div data-testid="what-changed-item">
      <Card
        interactive={false}
        className="flex flex-col gap-2"
      >
        <div className="flex items-center justify-between gap-2">
          <h3 className="font-display text-base font-semibold">{item.title}</h3>
          <Badge variant="default">{occurredAt}</Badge>
        </div>
        <p className="text-c3 text-sm leading-relaxed">{item.summary}</p>
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="default">
            {IMPORTANCE_LABELS[item.importance] ?? item.importance}
          </Badge>
          <span className="text-c4 text-xs">{item.source}</span>
        </div>
        <Link
          href={item.path}
          className="text-gold3 hover:text-gold text-sm transition-colors duration-300"
        >
          Подробнее <ArrowNext />
        </Link>
      </Card>
    </div>
  );
}
