import type { CountryListResponse } from "../../shared/api/countries";
import type { SearchResultItem } from "../../shared/api/search";

const ENTITY_TYPE_OPTIONS: Array<{
  value: SearchResultItem["entity_type"];
  label: string;
}> = [
  { value: "country", label: "Страны" },
  { value: "route", label: "Маршруты" },
  { value: "route_checklist_item", label: "Пункты чек-листа" },
  { value: "legal_signal", label: "Правовые сигналы" },
  { value: "source", label: "Источники" },
  { value: "evidence_item", label: "Доказательства" },
  { value: "country_pair_compatibility", label: "Совместимость стран" },
  { value: "methodology", label: "Методология" },
  { value: "glossary_term", label: "Термины глоссария" },
];

export function SearchFilters({
  selectedTypes,
  countrySlug,
  countries,
  onToggleType,
  onCountryChange,
}: {
  selectedTypes: string[];
  countrySlug: string;
  countries: CountryListResponse["items"];
  onToggleType: (type: string) => void;
  onCountryChange: (countrySlug: string) => void;
}) {
  return (
    <div
      className="border-warm bg-bg2 flex flex-col gap-4 border p-4 sm:flex-row sm:items-start sm:justify-between"
      data-testid="search-filters"
    >
      <div className="flex flex-col gap-2">
        <span className="font-mono text-c4 text-[9px] tracking-[0.2em] uppercase">
          Тип результата
        </span>
        <div className="flex flex-wrap gap-x-4 gap-y-2">
          {ENTITY_TYPE_OPTIONS.map((option) => (
            <label
              key={option.value}
              className="text-c2 flex cursor-pointer items-center gap-1.5 text-xs"
            >
              <input
                type="checkbox"
                checked={selectedTypes.includes(option.value)}
                onChange={() => onToggleType(option.value)}
                data-testid={`search-type-filter-${option.value}`}
                className="accent-gold"
              />
              {option.label}
            </label>
          ))}
        </div>
      </div>
      <label className="flex flex-col gap-2">
        <span className="font-mono text-c4 text-[9px] tracking-[0.2em] uppercase">
          Страна
        </span>
        <select
          className="border-warm bg-bg3 text-c2 border px-3 py-2 text-sm outline-none"
          value={countrySlug}
          onChange={(event) => onCountryChange(event.target.value)}
          data-testid="search-country-filter"
        >
          <option value="">Все страны</option>
          {countries.map((country) => (
            <option
              key={country.slug}
              value={country.slug}
            >
              {country.name}
            </option>
          ))}
        </select>
      </label>
    </div>
  );
}
