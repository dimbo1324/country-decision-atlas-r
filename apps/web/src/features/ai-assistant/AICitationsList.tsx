import { Badge, Kicker } from "@country-decision-atlas/ui";
import type { AICitation } from "../../shared/api/ai";
import { Link } from "../../i18n/navigation";

type AICitationsListProps = {
  citations?: AICitation[];
};

export function AICitationsList({ citations }: AICitationsListProps) {
  const items = citations ?? [];

  if (items.length === 0) {
    return null;
  }

  return (
    <div
      className="flex flex-col gap-2"
      data-testid="ai-citations"
    >
      <Kicker>Источники</Kicker>
      <ul className="flex flex-col gap-1.5">
        {items.map((citation) => (
          <li
            key={`${citation.entity_type}-${citation.entity_id}`}
            className="flex flex-wrap items-center gap-2 text-sm"
          >
            {citation.url_path ? (
              <Link
                href={citation.url_path}
                className="text-c1 hover:text-gold3 underline decoration-dotted underline-offset-2 transition-colors duration-200"
              >
                {citation.title}
              </Link>
            ) : (
              <span className="text-c2">{citation.title}</span>
            )}
            <Badge variant="default">
              {citation.entity_type}
              {citation.country_slug ? ` · ${citation.country_slug}` : ""}
            </Badge>
          </li>
        ))}
      </ul>
    </div>
  );
}
