import type { components } from "@country-decision-atlas/contracts/generated/types";

import { DEFAULT_API_LOCALE } from "../lib/locale";
import { apiGet, queryString } from "./http";

type LocaleCode = components["schemas"]["LocaleCode"];
export type CountryDataJournalResponse =
  components["schemas"]["CountryDataJournalResponse"];
export type DataJournalEntry = components["schemas"]["DataJournalEntry"];

export function getCountryDataJournal(
  countrySlug: string,
  locale: LocaleCode = DEFAULT_API_LOCALE,
  limit = 10,
  offset = 0,
): Promise<CountryDataJournalResponse> {
  return apiGet<CountryDataJournalResponse>(
    `/api/v1/countries/${countrySlug}/data-journal${queryString({
      locale,
      limit,
      offset,
    })}`,
  );
}

export const dataJournalApi = {
  getCountryDataJournal,
};
