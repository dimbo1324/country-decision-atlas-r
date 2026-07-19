import { useTranslations } from "next-intl";
import { FilterChipGroup } from "@country-decision-atlas/ui";
import type { CountryListResponse } from "../../shared/api/countries";
import { capitalize } from "../../shared/lib/format";
import type { SupportedLocale } from "../../shared/lib/locale";
import { useAppLocale } from "../../shared/lib/useAppLocale";
import { confidenceLabel } from "../../shared/ui/ConfidenceBadge";

const SOURCE_TYPE_VALUES = [
  "government",
  "news",
  "academic",
  "ngo",
  "legal",
  "official",
  "other",
] as const;

const SOURCE_TYPE_LABELS: Record<SupportedLocale, Record<string, string>> = {
  en: {
    government: "Government",
    news: "News",
    academic: "Academic",
    ngo: "NGO",
    legal: "Legal",
    official: "Official",
    other: "Other",
  },
  ru: {
    government: "Государственный",
    news: "СМИ",
    academic: "Научный",
    ngo: "НКО",
    legal: "Юридический",
    official: "Официальный",
    other: "Другое",
  },
  es: {
    government: "Gubernamental",
    news: "Medios",
    academic: "Académico",
    ngo: "ONG",
    legal: "Legal",
    official: "Oficial",
    other: "Otro",
  },
};

const CONFIDENCE_OPTIONS = ["high", "medium", "low"];

export function SourcesFilters({
  countrySlug,
  sourceType,
  confidence,
  countries,
  onCountryChange,
  onSourceTypeChange,
  onConfidenceChange,
}: {
  countrySlug: string;
  sourceType: string;
  confidence: string;
  countries: CountryListResponse["items"];
  onCountryChange: (value: string) => void;
  onSourceTypeChange: (value: string) => void;
  onConfidenceChange: (value: string) => void;
}) {
  const t = useTranslations("sourcesFilters");
  const locale = useAppLocale();
  return (
    <div
      className="border-warm flex flex-wrap gap-5 border p-4"
      data-testid="sources-filters"
    >
      <FilterChipGroup
        name="src-country"
        label={t("country")}
        value={countrySlug}
        onChange={onCountryChange}
        options={[
          { value: "", label: t("allCountries") },
          ...countries.map((country) => ({
            value: country.slug,
            label: country.name,
          })),
        ]}
      />
      <FilterChipGroup
        name="src-type"
        label={t("sourceType")}
        value={sourceType}
        onChange={onSourceTypeChange}
        options={[
          { value: "", label: t("allTypes") },
          ...SOURCE_TYPE_VALUES.map((type) => ({
            value: type,
            label: SOURCE_TYPE_LABELS[locale][type],
          })),
        ]}
      />
      <FilterChipGroup
        name="src-confidence"
        label={t("confidence")}
        value={confidence}
        onChange={onConfidenceChange}
        options={[
          { value: "", label: t("allLevels") },
          ...CONFIDENCE_OPTIONS.map((option) => ({
            value: option,
            label: capitalize(confidenceLabel(option, locale)),
          })),
        ]}
      />
    </div>
  );
}
