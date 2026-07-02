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
    <div className="filterBar searchFilters" data-testid="search-filters">
      <div className="filterGroup">
        <span className="filterLabel">Тип результата</span>
        <div className="searchTypeFilterList">
          {ENTITY_TYPE_OPTIONS.map((option) => (
            <label key={option.value} className="searchTypeFilterOption">
              <input
                type="checkbox"
                checked={selectedTypes.includes(option.value)}
                onChange={() => onToggleType(option.value)}
                data-testid={`search-type-filter-${option.value}`}
              />
              {option.label}
            </label>
          ))}
        </div>
      </div>
      <label className="filterGroup">
        <span className="filterLabel">Страна</span>
        <select
          className="filterSelect"
          value={countrySlug}
          onChange={(event) => onCountryChange(event.target.value)}
          data-testid="search-country-filter"
        >
          <option value="">Все страны</option>
          {countries.map((country) => (
            <option key={country.slug} value={country.slug}>
              {country.name}
            </option>
          ))}
        </select>
      </label>
    </div>
  );
}
