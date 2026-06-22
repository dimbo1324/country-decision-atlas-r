import type { CountryListResponse } from "../../shared/api/countries";

type Filters = {
  countrySlug: string;
  signalType: string;
  impactDirection: string;
  impactLevel: string;
  year: string;
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
  return (
    <div className="filterBar timelineFilters" data-testid="timeline-filters">
      <label>
        Страна
        <select
          id="timeline-country"
          value={filters.countrySlug}
          onChange={(event) => onChange("countrySlug", event.target.value)}
        >
          <option value="">Все страны</option>
          {countries.map((country) => (
            <option key={country.slug} value={country.slug}>
              {country.name}
            </option>
          ))}
        </select>
      </label>
      <label>
        Тип сигнала
        <select
          value={filters.signalType}
          onChange={(event) => onChange("signalType", event.target.value)}
        >
          <option value="">Все типы</option>
          <option value="law">Закон</option>
          <option value="bill">Законопроект</option>
          <option value="policy">Политика</option>
          <option value="court_decision">Судебное решение</option>
          <option value="administrative_change">Административное изменение</option>
          <option value="political_signal">Политический сигнал</option>
          <option value="other">Другое</option>
        </select>
      </label>
      <label>
        Направление влияния
        <select
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
      <label>
        Уровень влияния
        <select
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
      <label>
        Год
        <select
          value={filters.year}
          onChange={(event) => onChange("year", event.target.value)}
        >
          <option value="">Все годы</option>
          {years.map((year) => (
            <option key={year} value={year}>
              {year}
            </option>
          ))}
        </select>
      </label>
    </div>
  );
}

export type { Filters as TimelineFilterValues };
