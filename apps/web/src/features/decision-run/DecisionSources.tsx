import type { DecisionRunResponse } from "../../shared/api/decision";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ConfidenceBadge } from "../../shared/ui/ConfidenceBadge";

type DecisionSource = DecisionRunResponse["results"][number]["sources"][number];

type DecisionSourcesProps = {
  sources: DecisionSource[];
};

export function DecisionSources({ sources }: DecisionSourcesProps) {
  if (sources.length === 0) {
    return <EmptyState message="No sources are attached to this result." />;
  }

  return (
    <div className="sourceList">
      {sources.map((source) => (
        <div key={source.id} className="sourceCard">
          <div className="sourceCardHeader">
            <span className="sourceTitle">{source.title}</span>
            <div className="metaRow">
              {source.source_type && (
                <span className="metaChip">{source.source_type}</span>
              )}
              {source.confidence && <ConfidenceBadge confidence={source.confidence} />}
            </div>
          </div>
          <a href={source.url} target="_blank" rel="noreferrer" className="sourceLink">
            Open source ↗
          </a>
        </div>
      ))}
    </div>
  );
}
