import type { AICitation } from "../../shared/api/ai";

type AICitationsListProps = {
  citations?: AICitation[];
};

export function AICitationsList({ citations }: AICitationsListProps) {
  const items = citations ?? [];

  if (items.length === 0) {
    return null;
  }

  return (
    <div data-testid="ai-citations">
      <h3 className="resultSectionTitle">Источники</h3>
      <ul className="pointsList">
        {items.map((citation) => (
          <li key={`${citation.entity_type}-${citation.entity_id}`}>
            {citation.url_path ? (
              <a
                className="internalLink"
                href={citation.url_path}
              >
                {citation.title}
              </a>
            ) : (
              <span>{citation.title}</span>
            )}
            <span className="formHint">
              {" "}
              {citation.entity_type}
              {citation.country_slug ? ` · ${citation.country_slug}` : ""}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
