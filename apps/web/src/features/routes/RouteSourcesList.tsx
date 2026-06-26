import type { RouteDetailResponse } from "../../shared/api/routes";
import { RouteEmptyState } from "./RouteEmptyState";

type RouteSourcesListProps = {
  sources: RouteDetailResponse["sources"];
};

export function RouteSourcesList({ sources }: RouteSourcesListProps) {
  if (sources.length === 0) {
    return <RouteEmptyState message="Источники для этого маршрута пока не указаны." />;
  }

  return (
    <div className="routeSources">
      {sources.map((source) => (
        <a key={source.id} href={source.url} target="_blank" rel="noreferrer">
          <strong>{source.title}</strong>
          <span>
            {[source.source_type, source.publisher, source.confidence]
              .filter(Boolean)
              .join(" · ")}
          </span>
        </a>
      ))}
    </div>
  );
}
