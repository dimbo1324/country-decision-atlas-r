import Link from "next/link";

import type { WhatChangedItem } from "../../shared/api/what-changed";

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
  const occurredAt = new Date(item.occurred_at).toLocaleDateString("ru-RU");

  return (
    <article
      className="sourceCard"
      data-testid="what-changed-item"
    >
      <div className="sourceCardHeader">
        <h3>{item.title}</h3>
        <span className="metaChip">{occurredAt}</span>
      </div>
      <p>{item.summary}</p>
      <div className="sourceMeta">
        <span className="metaChip">
          {IMPORTANCE_LABELS[item.importance] ?? item.importance}
        </span>
        <span>{item.source}</span>
      </div>
      <Link
        href={item.path}
        className="internalLink"
      >
        Подробнее →
      </Link>
    </article>
  );
}
