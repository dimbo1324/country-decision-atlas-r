import type { CountryReadModelResponse } from "../../shared/api/countries";
import { EmptyState } from "../../shared/ui/EmptyState";
import { formatDate } from "../../shared/lib/format";

type CountryLegalSignalsProps = {
  legalSignals: CountryReadModelResponse["legal_signals"];
};

export function CountryLegalSignals({
  legalSignals,
}: CountryLegalSignalsProps) {
  if (!legalSignals || legalSignals.length === 0) return <EmptyState />;

  return (
    <div className="signalList">
      {legalSignals.map((signal) => (
        <div key={signal.id} className="signalCard">
          <div className="signalCardHeader">
            <span className="signalTitle">{signal.title}</span>
            <span className="metaChip">{signal.signal_type}</span>
          </div>
          {signal.summary && <p>{signal.summary}</p>}
          <div className="metaRow">
            {signal.impact_direction && (
              <span className="metaChip">Direction: {signal.impact_direction}</span>
            )}
            {signal.impact_level && (
              <span className="metaChip">Level: {signal.impact_level}</span>
            )}
            {signal.confidence && (
              <span className="metaChip">Confidence: {signal.confidence}</span>
            )}
            {signal.published_date && (
              <span className="metaChip">
                Published: {formatDate(signal.published_date)}
              </span>
            )}
            {signal.effective_date && (
              <span className="metaChip">
                Effective: {formatDate(signal.effective_date)}
              </span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
