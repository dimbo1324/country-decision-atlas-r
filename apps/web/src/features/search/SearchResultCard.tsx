import NextLink from "next/link";
import { Badge, Card } from "@country-decision-atlas/ui";
import { Link } from "../../i18n/navigation";
import type { SearchResultItem } from "../../shared/api/search";
import { entityTypeLabel } from "../../shared/lib/entity-type-labels";
import { useAppLocale } from "../../shared/lib/useAppLocale";

function stripHighlightTags(snippet: string): string {
  return snippet.replace(/<[^>]+>/g, "");
}

export function SearchResultCard({ item }: { item: SearchResultItem }) {
  const locale = useAppLocale();
  const isExternalPath = !item.path.startsWith("/");
  const LinkComponent = isExternalPath ? NextLink : Link;

  return (
    <div data-testid="search-result-card">
      <Card
        interactive={false}
        className="flex flex-col gap-2"
      >
        <div className="flex items-center gap-2">
          <Badge variant="info">
            {entityTypeLabel(item.entity_type, locale)}
          </Badge>
          {item.country_slug && (
            <Badge variant="default">{item.country_slug}</Badge>
          )}
        </div>
        <LinkComponent
          href={item.path}
          className="font-display text-gold3 hover:text-gold text-base font-semibold transition-colors duration-300"
          data-testid="search-result-link"
        >
          {item.title}
        </LinkComponent>
        <p className="text-c3 text-sm leading-relaxed">
          {stripHighlightTags(item.snippet)}
        </p>
      </Card>
    </div>
  );
}
