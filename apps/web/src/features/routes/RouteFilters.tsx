import type { EligibilityFlag, RouteType } from "../../shared/api/routes";

export type RouteFilterValues = {
  route_type: RouteType | "";
  allows_work: EligibilityFlag | "";
  allows_family: EligibilityFlag | "";
  leads_to_pr: EligibilityFlag | "";
};

const ROUTE_TYPES: { value: RouteType; label: string }[] = [
  { value: "temporary_residence", label: "Временное проживание" },
  { value: "permanent_residence", label: "ПМЖ" },
  { value: "citizenship", label: "Гражданство" },
  { value: "digital_nomad", label: "Digital nomad" },
  { value: "work", label: "Работа" },
  { value: "business", label: "Бизнес" },
  { value: "study", label: "Учёба" },
  { value: "investment", label: "Инвестиции" },
];

const ELIGIBILITY_OPTIONS: { value: EligibilityFlag; label: string }[] = [
  { value: "yes", label: "Да" },
  { value: "no", label: "Нет" },
  { value: "unknown", label: "Неизвестно" },
];

type RouteFiltersProps = {
  filters: RouteFilterValues;
  onChange: (name: keyof RouteFilterValues, value: string) => void;
};

export function RouteFilters({ filters, onChange }: RouteFiltersProps) {
  return (
    <div className="filterBar routeFilters" data-testid="route-filters">
      <label>
        Тип маршрута
        <select
          value={filters.route_type}
          onChange={(event) => onChange("route_type", event.target.value)}
        >
          <option value="">Все типы</option>
          {ROUTE_TYPES.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>
      <label>
        Работа
        <select
          value={filters.allows_work}
          onChange={(event) => onChange("allows_work", event.target.value)}
        >
          <option value="">Любой статус</option>
          {ELIGIBILITY_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>
      <label>
        Семья
        <select
          value={filters.allows_family}
          onChange={(event) => onChange("allows_family", event.target.value)}
        >
          <option value="">Любой статус</option>
          {ELIGIBILITY_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>
      <label>
        ПМЖ
        <select
          value={filters.leads_to_pr}
          onChange={(event) => onChange("leads_to_pr", event.target.value)}
        >
          <option value="">Любой статус</option>
          {ELIGIBILITY_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>
    </div>
  );
}
