import type { CountryReadModelResponse } from "../../shared/api/countries";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ImpactDirectionBadge, ImpactLevelBadge } from "../../shared/ui/ImpactBadge";
import { ConfidenceBadge } from "../../shared/ui/ConfidenceBadge";
import { formatDate } from "../../shared/lib/format";

type CountryLegalSignalsProps = {
  legalSignals: CountryReadModelResponse["legal_signals"];
};

export function CountryLegalSignals({ legalSignals }: CountryLegalSignalsProps) {
  if (!legalSignals || legalSignals.length === 0) {
    return <EmptyState message="Правовые сигналы для этой страны пока отсутствуют." />;
  }

  return (
    <div className="signalList">
      {legalSignals.map((signal) => (
        <div key={signal.id} className="signalCard">
          <div className="signalCardHeader">
            <span className="signalTitle">{signal.title}</span>
            <span className="metaChip">{signal.signal_type}</span>
          </div>
          {signal.summary && <p className="signalSummary">{signal.summary}</p>}
          <div className="metaRow">
            {signal.impact_direction && (
              <ImpactDirectionBadge direction={signal.impact_direction} />
            )}
            {signal.impact_level && <ImpactLevelBadge level={signal.impact_level} />}
            {signal.confidence && <ConfidenceBadge confidence={signal.confidence} />}
            {signal.published_date && (
              <span className="metaChip">
                Опубликовано: {formatDate(signal.published_date)}
              </span>
            )}
            {signal.effective_date && (
              <span className="metaChip">
                Действует с: {formatDate(signal.effective_date)}
              </span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
