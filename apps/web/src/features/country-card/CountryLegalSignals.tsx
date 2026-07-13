import { Badge, Card } from "@country-decision-atlas/ui";
import type { CountryReadModelResponse } from "../../shared/api/countries";
import { EmptyState } from "../../shared/ui/EmptyState";
import {
  ImpactDirectionBadge,
  ImpactLevelBadge,
} from "../../shared/ui/ImpactBadge";
import { ConfidenceBadge } from "../../shared/ui/ConfidenceBadge";
import { LocalizationBadge } from "../../shared/ui/LocalizationBadge";
import { formatDate } from "../../shared/lib/format";

type CountryLegalSignalsProps = {
  legalSignals: CountryReadModelResponse["legal_signals"];
};

export function CountryLegalSignals({
  legalSignals,
}: CountryLegalSignalsProps) {
  if (!legalSignals || legalSignals.length === 0) {
    return (
      <EmptyState message="Правовые сигналы для этой страны пока отсутствуют." />
    );
  }

  return (
    <div
      className="flex flex-col gap-4"
      data-testid="country-legal-signals"
    >
      {legalSignals.map((signal) => (
        <Card
          key={signal.id}
          interactive={false}
          className="flex flex-col gap-3"
        >
          <div className="flex flex-wrap items-center justify-between gap-2">
            <span className="font-display text-base font-semibold">
              {signal.title}
            </span>
            <div className="flex items-center gap-2">
              <Badge variant="default">{signal.signal_type}</Badge>
              <LocalizationBadge
                localization={signal.localization}
                compact
              />
            </div>
          </div>
          {signal.summary && (
            <p className="text-c3 text-sm leading-relaxed">{signal.summary}</p>
          )}
          <div className="flex flex-wrap gap-2">
            {signal.impact_direction && (
              <ImpactDirectionBadge direction={signal.impact_direction} />
            )}
            {signal.impact_level && (
              <ImpactLevelBadge level={signal.impact_level} />
            )}
            {signal.confidence && (
              <ConfidenceBadge confidence={signal.confidence} />
            )}
            {signal.published_date && (
              <Badge variant="default">
                Опубликовано: {formatDate(signal.published_date)}
              </Badge>
            )}
            {signal.effective_date && (
              <Badge variant="default">
                Действует с: {formatDate(signal.effective_date)}
              </Badge>
            )}
          </div>
        </Card>
      ))}
    </div>
  );
}
