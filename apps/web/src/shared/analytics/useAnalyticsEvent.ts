"use client";

import { useCallback } from "react";
import { useLocale } from "next-intl";
import { usePathname } from "../../i18n/navigation";
import { trackEvent, type AnalyticsEventInput } from "./client";

type TrackableEvent = Omit<AnalyticsEventInput, "path" | "locale"> &
  Partial<Pick<AnalyticsEventInput, "path" | "locale">>;

/** Thin wrapper over `trackEvent` that fills `path`/`locale` from the
 * current route so call sites only need to name the event itself. */
export function useAnalyticsEvent() {
  const pathname = usePathname();
  const locale = useLocale();

  return useCallback(
    (event: TrackableEvent) => {
      void trackEvent({
        path: pathname,
        locale,
        ...event,
      });
    },
    [pathname, locale],
  );
}
