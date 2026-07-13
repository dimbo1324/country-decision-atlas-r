import type { CountryListResponse } from "../../shared/api/countries";

const SOURCE_TYPES = [
  "government",
  "news",
  "academic",
  "ngo",
  "legal",
  "official",
  "other",
];

const CONFIDENCE_OPTIONS = ["high", "medium", "low"];

const SELECT_CLASS =
  "border-warm bg-bg2 text-c1 font-body border px-3 py-2 text-sm transition-colors duration-300 hover:border-[var(--color-c3)] focus:outline-none";
const LABEL_CLASS =
  "font-mono text-c3 flex flex-col gap-1.5 text-[9px] tracking-[0.15em] uppercase";

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
  return (
    <div
      className="border-warm flex flex-wrap gap-4 border p-4"
      data-testid="sources-filters"
    >
      <label className={LABEL_CLASS}>
        Страна
        <select
          id="src-country"
          className={SELECT_CLASS}
          value={countrySlug}
          onChange={(event) => onCountryChange(event.target.value)}
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
      <label className={LABEL_CLASS}>
        Тип источника
        <select
          id="src-type"
          className={SELECT_CLASS}
          value={sourceType}
          onChange={(event) => onSourceTypeChange(event.target.value)}
        >
          <option value="">Все типы</option>
          {SOURCE_TYPES.map((type) => (
            <option
              key={type}
              value={type}
            >
              {type}
            </option>
          ))}
        </select>
      </label>
      <label className={LABEL_CLASS}>
        Достоверность
        <select
          id="src-confidence"
          className={SELECT_CLASS}
          value={confidence}
          onChange={(event) => onConfidenceChange(event.target.value)}
        >
          <option value="">Все уровни</option>
          {CONFIDENCE_OPTIONS.map((option) => (
            <option
              key={option}
              value={option}
            >
              {option}
            </option>
          ))}
        </select>
      </label>
    </div>
  );
}
