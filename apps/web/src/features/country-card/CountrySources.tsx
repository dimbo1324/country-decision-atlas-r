import { Badge, Card } from "@country-decision-atlas/ui";
import type { CountryReadModelResponse } from "../../shared/api/countries";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ConfidenceBadge } from "../../shared/ui/ConfidenceBadge";
import { LocalizationBadge } from "../../shared/ui/LocalizationBadge";
import { formatDate } from "../../shared/lib/format";
import { useAppLocale } from "../../shared/lib/useAppLocale";
import { ArrowExternal } from "../../shared/ui/LinkArrow";

type CountrySourcesProps = {
  sources: CountryReadModelResponse["sources"];
};

export function CountrySources({ sources }: CountrySourcesProps) {
  const locale = useAppLocale();
  if (!sources || sources.length === 0) {
    return <EmptyState message="К этой стране источники не прикреплены." />;
  }

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
      {sources.map((source) => (
        <Card
          key={source.id}
          interactive={false}
          className="flex flex-col gap-2"
        >
          <div className="flex items-start justify-between gap-2">
            <span className="font-display text-base font-semibold">
              {source.title}
            </span>
            <LocalizationBadge
              localization={source.localization}
              compact
            />
          </div>
          <div className="flex flex-wrap gap-2">
            {source.source_type && (
              <Badge variant="default">{source.source_type}</Badge>
            )}
            {source.confidence && (
              <ConfidenceBadge confidence={source.confidence} />
            )}
          </div>
          {source.publisher && (
            <span className="text-c4 text-xs">{source.publisher}</span>
          )}
          <div className="flex flex-wrap gap-2">
            {source.last_checked_at && (
              <Badge variant="default">
                Проверено: {formatDate(source.last_checked_at, locale)}
              </Badge>
            )}
            {source.published_at && (
              <Badge variant="default">
                Опубликовано: {formatDate(source.published_at, locale)}
              </Badge>
            )}
          </div>
          <a
            href={source.url}
            target="_blank"
            rel="noreferrer"
            className="text-gold3 hover:text-gold text-sm transition-colors duration-300"
          >
            Открыть источник <ArrowExternal />
          </a>
        </Card>
      ))}
    </div>
  );
}
