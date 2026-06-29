import type { components } from "@country-decision-atlas/contracts/generated/types";

import { apiPost } from "../api/http";
import { getOrCreateAnonymousSessionId } from "./session";

export type AnalyticsEventInput = Omit<
  components["schemas"]["AnalyticsEventCreate"],
  "session_id"
>;
export type AnalyticsEventResponse =
  components["schemas"]["AnalyticsEventCreateResponse"];

export async function trackEvent(event: AnalyticsEventInput): Promise<void> {
  try {
    await apiPost<
      AnalyticsEventResponse,
      components["schemas"]["AnalyticsEventCreate"]
    >("/api/v1/analytics/events", {
      ...event,
      session_id: getOrCreateAnonymousSessionId(),
    });
  } catch {
    return;
  }
}
