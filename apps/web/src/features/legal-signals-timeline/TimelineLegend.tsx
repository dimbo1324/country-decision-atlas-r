import { Kicker } from "@country-decision-atlas/ui";
import { ImpactDirectionBadge } from "../../shared/ui/ImpactBadge";

const directions = [
  "positive",
  "negative",
  "neutral",
  "mixed",
  "uncertain",
] as const;

export function TimelineLegend() {
  return (
    <div
      className="flex flex-wrap items-center gap-3"
      data-testid="legal-signals-timeline-legend"
    >
      <Kicker>Направление влияния</Kicker>
      {directions.map((direction) => (
        <ImpactDirectionBadge
          key={direction}
          direction={direction}
        />
      ))}
    </div>
  );
}
