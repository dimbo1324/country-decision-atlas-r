import type { CountryReadModelResponse } from "../../shared/api/countries";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ConfidenceBadge } from "../../shared/ui/ConfidenceBadge";
import { LocalizationBadge } from "../../shared/ui/LocalizationBadge";
import { formatDate } from "../../shared/lib/format";

type CountrySourcesProps = {
  sources: CountryReadModelResponse["sources"];
};

export function CountrySources({ sources }: CountrySourcesProps) {
  if (!sources || sources.length === 0) {
    return <EmptyState message="К этой стране источники не прикреплены." />;
  }

  return (
    <div className="sourceList">
      {sources.map((source) => (
        <div
          key={source.id}
          className="sourceCard"
        >
          <div className="sourceCardHeader">
            <span className="sourceTitle">{source.title}</span>
            <div className="metaRow">
              {source.source_type && (
                <span className="metaChip">{source.source_type}</span>
              )}
              {source.confidence && (
                <ConfidenceBadge confidence={source.confidence} />
              )}
              <LocalizationBadge
                localization={source.localization}
                compact
              />
            </div>
          </div>
          {source.publisher && (
            <span className="sourcePublisher">{source.publisher}</span>
          )}
          <div className="metaRow">
            {source.last_checked_at && (
              <span className="metaChip">
                Проверено: {formatDate(source.last_checked_at)}
              </span>
            )}
            {source.published_at && (
              <span className="metaChip">
                Опубликовано: {formatDate(source.published_at)}
              </span>
            )}
          </div>
          <a
            href={source.url}
            target="_blank"
            rel="noreferrer"
            className="sourceLink"
          >
            Открыть источник ↗
          </a>
        </div>
      ))}
    </div>
  );
}
