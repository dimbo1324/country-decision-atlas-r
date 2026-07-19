import type { LegalSignalEvent } from "@country-decision-atlas/ui";
import type { LegalSignalTimelineEvent } from "../../shared/api/legal-signals";
import type { SupportedLocale } from "../../shared/lib/locale";
import { impactDirectionLabel } from "./impact-direction-labels";

const IMPACT_MAP: Record<string, LegalSignalEvent["impact"]> = {
  positive: "up",
  negative: "down",
};

/** The chart primitive (Stage 4) only distinguishes up/down/info — real
 * `impact_direction` has 5 values, so neutral/mixed/uncertain all collapse
 * to "info" for marker color while the tooltip/label keeps the real word. */
export function adaptTimelineEvents(
  events: LegalSignalTimelineEvent[],
  locale: SupportedLocale,
): LegalSignalEvent[] {
  return events.map((event) => ({
    id: event.id,
    date: event.event_date,
    country: event.country_name,
    title: event.title,
    impact: IMPACT_MAP[event.impact_direction] ?? "info",
    impactLabel: impactDirectionLabel(locale, event.impact_direction),
  }));
}
