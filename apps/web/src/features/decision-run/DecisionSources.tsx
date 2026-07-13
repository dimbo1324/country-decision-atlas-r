import { Badge } from "@country-decision-atlas/ui";
import type { DecisionRunResponse } from "../../shared/api/decision";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ConfidenceBadge } from "../../shared/ui/ConfidenceBadge";
import { LocalizationBadge } from "../../shared/ui/LocalizationBadge";

type DecisionSource = DecisionRunResponse["results"][number]["sources"][number];

type DecisionSourcesProps = {
  sources: DecisionSource[];
};

export function DecisionSources({ sources }: DecisionSourcesProps) {
  if (sources.length === 0) {
    return (
      <EmptyState message="К этому результату источники не прикреплены." />
    );
  }

  return (
    <div className="flex flex-col gap-3">
      {sources.map((source) => (
        <div
          key={source.id}
          className="border-warm flex flex-col gap-2 border-l-2 pl-3"
        >
          <div className="flex flex-wrap items-center justify-between gap-2">
            <span className="text-c2 text-sm">{source.title}</span>
            <div className="flex flex-wrap gap-2">
              {source.source_type && (
                <Badge variant="default">{source.source_type}</Badge>
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
          <a
            href={source.url}
            target="_blank"
            rel="noreferrer"
            className="text-gold3 hover:text-gold text-sm transition-colors duration-300"
          >
            Открыть источник ↗
          </a>
        </div>
      ))}
    </div>
  );
}
