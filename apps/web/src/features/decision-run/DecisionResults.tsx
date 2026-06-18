import type { DecisionRunResponse } from "../../shared/api/decision";
import { EmptyState } from "../../shared/ui/EmptyState";
import { DecisionResultCard } from "./DecisionResultCard";

type DecisionResultsProps = {
  response: DecisionRunResponse;
};

export function DecisionResults({ response }: DecisionResultsProps) {
  const { scenario, origin_country, results, meta, locale } = response;

  return (
    <div className="decisionResults">
      <div className="decisionResultsMeta">
        <div className="resultMetaRow">
          <span>Scenario:</span>
          <strong>{scenario.title}</strong>
        </div>
        <div className="resultMetaRow">
          <span>Origin:</span>
          <strong>{origin_country.name}</strong>
        </div>
        <div className="resultMetaRow">
          <span>Generated:</span>
          <span>{new Date(meta.generated_at).toLocaleString("en")}</span>
        </div>
        <div className="resultMetaRow">
          <span>Locale status:</span>
          <span className="metaChip">{locale.translation_status}</span>
        </div>
      </div>

      {results.length === 0 ? (
        <EmptyState />
      ) : (
        <div className="resultList">
          {results.map((result) => (
            <DecisionResultCard key={result.country.id} result={result} />
          ))}
        </div>
      )}
    </div>
  );
}
