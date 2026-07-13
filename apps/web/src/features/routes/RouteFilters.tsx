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
  onReset?: () => void;
};

const SELECT_CLASS =
  "border-warm bg-bg2 text-c2 focus-visible:border-gold w-full border px-2 py-1.5 text-sm outline-none";
const LABEL_CLASS =
  "font-mono text-c4 flex flex-col gap-1 text-[9px] tracking-[0.15em] uppercase";

export function RouteFilters({
  filters,
  onChange,
  onReset,
}: RouteFiltersProps) {
  return (
    <div
      className="flex flex-wrap items-end gap-4"
      data-testid="route-filters"
    >
      <label className={LABEL_CLASS}>
        Тип маршрута
        <select
          value={filters.route_type}
          data-testid="route-filter-route-type"
          onChange={(event) => onChange("route_type", event.target.value)}
          className={SELECT_CLASS}
        >
          <option value="">Все типы</option>
          {ROUTE_TYPES.map((option) => (
            <option
              key={option.value}
              value={option.value}
            >
              {option.label}
            </option>
          ))}
        </select>
      </label>
      <label className={LABEL_CLASS}>
        Работа
        <select
          value={filters.allows_work}
          data-testid="route-filter-allows-work"
          onChange={(event) => onChange("allows_work", event.target.value)}
          className={SELECT_CLASS}
        >
          <option value="">Любой статус</option>
          {ELIGIBILITY_OPTIONS.map((option) => (
            <option
              key={option.value}
              value={option.value}
            >
              {option.label}
            </option>
          ))}
        </select>
      </label>
      <label className={LABEL_CLASS}>
        Семья
        <select
          value={filters.allows_family}
          data-testid="route-filter-allows-family"
          onChange={(event) => onChange("allows_family", event.target.value)}
          className={SELECT_CLASS}
        >
          <option value="">Любой статус</option>
          {ELIGIBILITY_OPTIONS.map((option) => (
            <option
              key={option.value}
              value={option.value}
            >
              {option.label}
            </option>
          ))}
        </select>
      </label>
      <label className={LABEL_CLASS}>
        ПМЖ
        <select
          value={filters.leads_to_pr}
          data-testid="route-filter-leads-to-pr"
          onChange={(event) => onChange("leads_to_pr", event.target.value)}
          className={SELECT_CLASS}
        >
          <option value="">Любой статус</option>
          {ELIGIBILITY_OPTIONS.map((option) => (
            <option
              key={option.value}
              value={option.value}
            >
              {option.label}
            </option>
          ))}
        </select>
      </label>
      {onReset && (
        <button
          type="button"
          data-testid="route-filter-reset"
          onClick={onReset}
          className="font-mono text-c3 hover:text-gold border-warm border px-3 py-1.5 text-[9px] tracking-[0.15em] uppercase transition-colors duration-300"
        >
          Сбросить
        </button>
      )}
    </div>
  );
}
