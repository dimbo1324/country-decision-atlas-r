import { FilterChipGroup } from "@country-decision-atlas/ui";
import type { CountryListResponse } from "../../shared/api/countries";
import { capitalize } from "../../shared/lib/format";
import { useAppLocale } from "../../shared/lib/useAppLocale";
import { confidenceLabel } from "../../shared/ui/ConfidenceBadge";

const SOURCE_TYPE_LABELS: Record<string, string> = {
  government: "Государственный",
  news: "СМИ",
  academic: "Научный",
  ngo: "НКО",
  legal: "Юридический",
  official: "Официальный",
  other: "Другое",
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
  const locale = useAppLocale();
  return (
    <div
      className="border-warm flex flex-wrap gap-5 border p-4"
      data-testid="sources-filters"
    >
      <FilterChipGroup
        name="src-country"
        label="Страна"
        value={countrySlug}
        onChange={onCountryChange}
        options={[
          { value: "", label: "Все страны" },
          ...countries.map((country) => ({
            value: country.slug,
            label: country.name,
          })),
        ]}
      />
      <FilterChipGroup
        name="src-type"
        label="Тип источника"
        value={sourceType}
        onChange={onSourceTypeChange}
        options={[
          { value: "", label: "Все типы" },
          ...Object.keys(SOURCE_TYPE_LABELS).map((type) => ({
            value: type,
            label: SOURCE_TYPE_LABELS[type],
          })),
        ]}
      />
      <FilterChipGroup
        name="src-confidence"
        label="Достоверность"
        value={confidence}
        onChange={onConfidenceChange}
        options={[
          { value: "", label: "Все уровни" },
          ...CONFIDENCE_OPTIONS.map((option) => ({
            value: option,
            label: capitalize(confidenceLabel(option, locale)),
          })),
        ]}
      />
    </div>
  );
}
