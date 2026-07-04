import Link from "next/link";
import type { SearchResultItem } from "../../shared/api/search";
import { withLocale } from "../../shared/lib/routes";
import { Badge } from "../../shared/ui/Badge";

const ENTITY_TYPE_LABELS: Record<SearchResultItem["entity_type"], string> = {
  country: "Страна",
  route: "Маршрут",
  route_checklist_item: "Пункт чек-листа",
  legal_signal: "Правовой сигнал",
  source: "Источник",
  evidence_item: "Доказательство",
  country_pair_compatibility: "Совместимость стран",
  methodology: "Методология",
  glossary_term: "Термин глоссария",
};

function stripHighlightTags(snippet: string): string {
  return snippet.replace(/<[^>]+>/g, "");
}

export function SearchResultCard({
  item,
  locale,
}: {
  item: SearchResultItem;
  locale: string;
}) {
  const isExternalPath = !item.path.startsWith("/");
  const href = isExternalPath ? item.path : withLocale(item.path, locale);

  return (
    <div
      className="searchResultCard"
      data-testid="search-result-card"
    >
      <div className="searchResultCardHeader">
        <Badge variant="info">{ENTITY_TYPE_LABELS[item.entity_type]}</Badge>
        {item.country_slug && (
          <Badge variant="default">{item.country_slug}</Badge>
        )}
      </div>
      <Link
        href={href}
        className="searchResultTitle"
        data-testid="search-result-link"
      >
        {item.title}
      </Link>
      <p className="searchResultSnippet">{stripHighlightTags(item.snippet)}</p>
    </div>
  );
}
