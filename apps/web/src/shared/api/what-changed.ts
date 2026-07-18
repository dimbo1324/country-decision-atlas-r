import type { components } from "@country-decision-atlas/contracts/generated/types";

import { DEFAULT_API_LOCALE } from "../lib/locale";
import { apiGet, queryString } from "./http";

type LocaleCode = components["schemas"]["LocaleCode"];
export type WhatChangedItem = components["schemas"]["WhatChangedItem"];
export type WhatChangedSummary = components["schemas"]["WhatChangedSummary"];
export type WhatChangedResponse = components["schemas"]["WhatChangedResponse"];

type WhatChangedParams = {
  locale?: LocaleCode;
  since?: string;
  days?: number;
  limit?: number;
};

export function getCountryWhatChanged(
  countrySlug: string,
  params: WhatChangedParams = {},
): Promise<WhatChangedResponse> {
  return apiGet<WhatChangedResponse>(
    `/api/v1/countries/${countrySlug}/what-changed${queryString({
      locale: params.locale ?? DEFAULT_API_LOCALE,
      since: params.since,
      days: params.days,
      limit: params.limit,
    })}`,
  );
}

export const whatChangedApi = {
  getCountryWhatChanged,
};
