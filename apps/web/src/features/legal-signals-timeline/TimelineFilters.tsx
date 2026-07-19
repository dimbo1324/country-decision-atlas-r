import { useTranslations } from "next-intl";
import { FilterChipGroup } from "@country-decision-atlas/ui";
import type { CountryListResponse } from "../../shared/api/countries";
import type { SupportedLocale } from "../../shared/lib/locale";
import { useAppLocale } from "../../shared/lib/useAppLocale";
import { IMPACT_DIRECTION_LABELS } from "./impact-direction-labels";

type Filters = {
  countrySlug: string;
  signalType: string;
  impactDirection: string;
  impactLevel: string;
  year: string;
};

const SIGNAL_TYPE_VALUES = [
  "law",
  "bill",
  "policy",
  "court_decision",
  "administrative_change",
  "political_signal",
  "other",
] as const;

const SIGNAL_TYPE_LABELS: Record<SupportedLocale, Record<string, string>> = {
  en: {
    law: "Law",
    bill: "Bill",
    policy: "Policy",
    court_decision: "Court decision",
    administrative_change: "Administrative change",
    political_signal: "Political signal",
    other: "Other",
  },
  ru: {
    law: "Закон",
    bill: "Законопроект",
    policy: "Политика",
    court_decision: "Судебное решение",
    administrative_change: "Административное изменение",
    political_signal: "Политический сигнал",
    other: "Другое",
  },
  es: {
    law: "Ley",
    bill: "Proyecto de ley",
    policy: "Política",
    court_decision: "Decisión judicial",
    administrative_change: "Cambio administrativo",
    political_signal: "Señal política",
    other: "Otro",
  },
};

const IMPACT_DIRECTION_VALUES = [
  "positive",
  "negative",
  "neutral",
  "mixed",
  "uncertain",
] as const;

const IMPACT_LEVEL_VALUES = ["low", "medium", "high", "critical"] as const;

const IMPACT_LEVEL_LABELS: Record<SupportedLocale, Record<string, string>> = {
  en: { low: "Low", medium: "Medium", high: "High", critical: "Critical" },
  ru: {
    low: "Низкий",
    medium: "Средний",
    high: "Высокий",
    critical: "Критический",
  },
  es: { low: "Bajo", medium: "Medio", high: "Alto", critical: "Crítico" },
};

export function TimelineFilters({
  filters,
  countries,
  years,
  onChange,
}: {
  filters: Filters;
  countries: CountryListResponse["items"];
  years: number[];
  onChange: (name: keyof Filters, value: string) => void;
}) {
  const t = useTranslations("legalSignalsTimeline");
  const locale = useAppLocale();

  const signalTypeOptions = [
    { value: "", label: t("allTypes") },
    ...SIGNAL_TYPE_VALUES.map((value) => ({
      value,
      label: SIGNAL_TYPE_LABELS[locale][value],
    })),
  ];
  const impactDirectionOptions = [
    { value: "", label: t("allDirections") },
    ...IMPACT_DIRECTION_VALUES.map((value) => ({
      value,
      label: IMPACT_DIRECTION_LABELS[locale][value],
    })),
  ];
  const impactLevelOptions = [
    { value: "", label: t("allLevels") },
    ...IMPACT_LEVEL_VALUES.map((value) => ({
      value,
      label: IMPACT_LEVEL_LABELS[locale][value],
    })),
  ];

  return (
    <div
      className="border-warm flex flex-wrap gap-5 border p-4"
      data-testid="timeline-filters"
    >
      <FilterChipGroup
        name="timeline-country"
        label={t("country")}
        value={filters.countrySlug}
        onChange={(value) => onChange("countrySlug", value)}
        options={[
          { value: "", label: t("allCountries") },
          ...countries.map((country) => ({
            value: country.slug,
            label: country.name,
          })),
        ]}
      />
      <FilterChipGroup
        name="timeline-signal-type"
        label={t("signalType")}
        value={filters.signalType}
        onChange={(value) => onChange("signalType", value)}
        options={signalTypeOptions}
      />
      <FilterChipGroup
        name="timeline-impact-direction"
        label={t("impactDirection")}
        value={filters.impactDirection}
        onChange={(value) => onChange("impactDirection", value)}
        options={impactDirectionOptions}
      />
      <FilterChipGroup
        name="timeline-impact-level"
        label={t("impactLevel")}
        value={filters.impactLevel}
        onChange={(value) => onChange("impactLevel", value)}
        options={impactLevelOptions}
      />
      <FilterChipGroup
        name="timeline-year"
        label={t("year")}
        value={filters.year}
        onChange={(value) => onChange("year", value)}
        options={[
          { value: "", label: t("allYears") },
          ...years.map((year) => ({
            value: String(year),
            label: String(year),
          })),
        ]}
      />
    </div>
  );
}

export type { Filters as TimelineFilterValues };
