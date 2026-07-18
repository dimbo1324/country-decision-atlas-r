import { FilterChipGroup } from "@country-decision-atlas/ui";
import type { CountryListResponse } from "../../shared/api/countries";

type Filters = {
  countrySlug: string;
  signalType: string;
  impactDirection: string;
  impactLevel: string;
  year: string;
};

const SIGNAL_TYPE_OPTIONS = [
  { value: "", label: "Все типы" },
  { value: "law", label: "Закон" },
  { value: "bill", label: "Законопроект" },
  { value: "policy", label: "Политика" },
  { value: "court_decision", label: "Судебное решение" },
  { value: "administrative_change", label: "Административное изменение" },
  { value: "political_signal", label: "Политический сигнал" },
  { value: "other", label: "Другое" },
];

const IMPACT_DIRECTION_OPTIONS = [
  { value: "", label: "Все направления" },
  { value: "positive", label: "Положительное" },
  { value: "negative", label: "Негативное" },
  { value: "neutral", label: "Нейтральное" },
  { value: "mixed", label: "Смешанное" },
  { value: "uncertain", label: "Неопределённое" },
];

const IMPACT_LEVEL_OPTIONS = [
  { value: "", label: "Все уровни" },
  { value: "low", label: "Низкий" },
  { value: "medium", label: "Средний" },
  { value: "high", label: "Высокий" },
  { value: "critical", label: "Критический" },
];

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
  return (
    <div
      className="border-warm flex flex-wrap gap-5 border p-4"
      data-testid="timeline-filters"
    >
      <FilterChipGroup
        name="timeline-country"
        label="Страна"
        value={filters.countrySlug}
        onChange={(value) => onChange("countrySlug", value)}
        options={[
          { value: "", label: "Все страны" },
          ...countries.map((country) => ({
            value: country.slug,
            label: country.name,
          })),
        ]}
      />
      <FilterChipGroup
        name="timeline-signal-type"
        label="Тип сигнала"
        value={filters.signalType}
        onChange={(value) => onChange("signalType", value)}
        options={SIGNAL_TYPE_OPTIONS}
      />
      <FilterChipGroup
        name="timeline-impact-direction"
        label="Направление влияния"
        value={filters.impactDirection}
        onChange={(value) => onChange("impactDirection", value)}
        options={IMPACT_DIRECTION_OPTIONS}
      />
      <FilterChipGroup
        name="timeline-impact-level"
        label="Уровень влияния"
        value={filters.impactLevel}
        onChange={(value) => onChange("impactLevel", value)}
        options={IMPACT_LEVEL_OPTIONS}
      />
      <FilterChipGroup
        name="timeline-year"
        label="Год"
        value={filters.year}
        onChange={(value) => onChange("year", value)}
        options={[
          { value: "", label: "Все годы" },
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
