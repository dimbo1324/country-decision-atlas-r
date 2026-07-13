import { queryOptions } from "@tanstack/react-query";
import type { components } from "@country-decision-atlas/contracts/generated/types";
import { dataJournalApi } from "../../shared/api/data-journal";

type LocaleCode = components["schemas"]["LocaleCode"];

export function countryDataJournalQuery(
  countrySlug: string,
  locale: LocaleCode,
) {
  return queryOptions({
    queryKey: ["country", countrySlug, "data-journal", locale] as const,
    queryFn: () => dataJournalApi.getCountryDataJournal(countrySlug, locale),
    staleTime: 60_000,
    retry: false,
  });
}
