import type { CountryListResponse } from "../../shared/api/countries";

type Filters = {
  countrySlug: string;
  signalType: string;
  impactDirection: string;
  impactLevel: string;
  year: string;
};

const SELECT_CLASS =
  "border-warm bg-bg2 text-c1 font-body border px-3 py-2 text-sm transition-colors duration-300 hover:border-[var(--color-c3)] focus:outline-none";
const LABEL_CLASS =
  "font-mono text-c3 flex flex-col gap-1.5 text-[9px] tracking-[0.15em] uppercase";

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
      className="border-warm flex flex-wrap gap-4 border p-4"
      data-testid="timeline-filters"
    >
      <label className={LABEL_CLASS}>
        Страна
        <select
          id="timeline-country"
          className={SELECT_CLASS}
          value={filters.countrySlug}
          onChange={(event) => onChange("countrySlug", event.target.value)}
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
        Тип сигнала
        <select
          className={SELECT_CLASS}
          value={filters.signalType}
          onChange={(event) => onChange("signalType", event.target.value)}
        >
          <option value="">Все типы</option>
          <option value="law">Закон</option>
          <option value="bill">Законопроект</option>
          <option value="policy">Политика</option>
          <option value="court_decision">Судебное решение</option>
          <option value="administrative_change">
            Административное изменение
          </option>
          <option value="political_signal">Политический сигнал</option>
          <option value="other">Другое</option>
        </select>
      </label>
      <label className={LABEL_CLASS}>
        Направление влияния
        <select
          className={SELECT_CLASS}
          value={filters.impactDirection}
          onChange={(event) => onChange("impactDirection", event.target.value)}
        >
          <option value="">Все направления</option>
          <option value="positive">Положительное</option>
          <option value="negative">Негативное</option>
          <option value="neutral">Нейтральное</option>
          <option value="mixed">Смешанное</option>
          <option value="uncertain">Неопределённое</option>
        </select>
      </label>
      <label className={LABEL_CLASS}>
        Уровень влияния
        <select
          className={SELECT_CLASS}
          value={filters.impactLevel}
          onChange={(event) => onChange("impactLevel", event.target.value)}
        >
          <option value="">Все уровни</option>
          <option value="low">Низкий</option>
          <option value="medium">Средний</option>
          <option value="high">Высокий</option>
          <option value="critical">Критический</option>
        </select>
      </label>
      <label className={LABEL_CLASS}>
        Год
        <select
          className={SELECT_CLASS}
          value={filters.year}
          onChange={(event) => onChange("year", event.target.value)}
        >
          <option value="">Все годы</option>
          {years.map((year) => (
            <option
              key={year}
              value={year}
            >
              {year}
            </option>
          ))}
        </select>
      </label>
    </div>
  );
}

export type { Filters as TimelineFilterValues };
