import { useTranslations } from "next-intl";
import type { CountryListResponse } from "../../shared/api/countries";
import type { SearchResultItem } from "../../shared/api/search";
import { entityTypeLabel } from "../../shared/lib/entity-type-labels";
import { useAppLocale } from "../../shared/lib/useAppLocale";

const ENTITY_TYPE_VALUES: SearchResultItem["entity_type"][] = [
  "country",
  "route",
  "route_checklist_item",
  "legal_signal",
  "source",
  "evidence_item",
  "country_pair_compatibility",
  "methodology",
  "glossary_term",
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
  const locale = useAppLocale();
  const t = useTranslations("searchFilters");
  return (
    <div
      className="border-warm bg-bg2 flex flex-col gap-4 border p-4 sm:flex-row sm:items-start sm:justify-between"
      data-testid="search-filters"
    >
      <div className="flex flex-col gap-2">
        <span className="font-mono text-c4 text-[9px] tracking-[0.2em] uppercase">
          {t("resultTypeLabel")}
        </span>
        <div className="flex flex-wrap gap-x-4 gap-y-2">
          {ENTITY_TYPE_VALUES.map((value) => (
            <label
              key={value}
              className="text-c2 flex cursor-pointer items-center gap-1.5 text-xs"
            >
              <input
                type="checkbox"
                checked={selectedTypes.includes(value)}
                onChange={() => onToggleType(value)}
                data-testid={`search-type-filter-${value}`}
                className="accent-gold"
              />
              {entityTypeLabel(value, locale)}
            </label>
          ))}
        </div>
      </div>
      <label className="flex flex-col gap-2">
        <span className="font-mono text-c4 text-[9px] tracking-[0.2em] uppercase">
          {t("countryLabel")}
        </span>
        <select
          className="border-warm bg-bg3 text-c2 border px-3 py-2 text-sm outline-none"
          value={countrySlug}
          onChange={(event) => onCountryChange(event.target.value)}
          data-testid="search-country-filter"
        >
          <option value="">{t("allCountries")}</option>
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
