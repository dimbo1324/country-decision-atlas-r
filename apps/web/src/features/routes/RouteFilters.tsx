import { useTranslations } from "next-intl";
import type { EligibilityFlag, RouteType } from "../../shared/api/routes";
import { useAppLocale } from "../../shared/lib/useAppLocale";
import { ROUTE_TYPE_LABELS } from "./route-labels";

export type RouteFilterValues = {
  route_type: RouteType | "";
  allows_work: EligibilityFlag | "";
  allows_family: EligibilityFlag | "";
  leads_to_pr: EligibilityFlag | "";
};

// Derived rather than a second hardcoded list -- ROUTE_TYPE_LABELS.en is
// keyed by the exact same RouteType union, so this can't drift out of sync.
const ROUTE_TYPE_VALUES = Object.keys(ROUTE_TYPE_LABELS.en) as RouteType[];

const ELIGIBILITY_VALUES: EligibilityFlag[] = ["yes", "no", "unknown"];

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
  const t = useTranslations("routes");
  const locale = useAppLocale();

  const eligibilityLabel = (value: EligibilityFlag) =>
    value === "yes" ? t("yes") : value === "no" ? t("no") : t("unknown");

  return (
    <div
      className="flex flex-wrap items-end gap-4"
      data-testid="route-filters"
    >
      <label className={LABEL_CLASS}>
        {t("routeType")}
        <select
          value={filters.route_type}
          data-testid="route-filter-route-type"
          onChange={(event) => onChange("route_type", event.target.value)}
          className={SELECT_CLASS}
        >
          <option value="">{t("allTypes")}</option>
          {ROUTE_TYPE_VALUES.map((value) => (
            <option
              key={value}
              value={value}
            >
              {ROUTE_TYPE_LABELS[locale][value]}
            </option>
          ))}
        </select>
      </label>
      <label className={LABEL_CLASS}>
        {t("work")}
        <select
          value={filters.allows_work}
          data-testid="route-filter-allows-work"
          onChange={(event) => onChange("allows_work", event.target.value)}
          className={SELECT_CLASS}
        >
          <option value="">{t("anyStatus")}</option>
          {ELIGIBILITY_VALUES.map((value) => (
            <option
              key={value}
              value={value}
            >
              {eligibilityLabel(value)}
            </option>
          ))}
        </select>
      </label>
      <label className={LABEL_CLASS}>
        {t("family")}
        <select
          value={filters.allows_family}
          data-testid="route-filter-allows-family"
          onChange={(event) => onChange("allows_family", event.target.value)}
          className={SELECT_CLASS}
        >
          <option value="">{t("anyStatus")}</option>
          {ELIGIBILITY_VALUES.map((value) => (
            <option
              key={value}
              value={value}
            >
              {eligibilityLabel(value)}
            </option>
          ))}
        </select>
      </label>
      <label className={LABEL_CLASS}>
        {t("permanentResidence")}
        <select
          value={filters.leads_to_pr}
          data-testid="route-filter-leads-to-pr"
          onChange={(event) => onChange("leads_to_pr", event.target.value)}
          className={SELECT_CLASS}
        >
          <option value="">{t("anyStatus")}</option>
          {ELIGIBILITY_VALUES.map((value) => (
            <option
              key={value}
              value={value}
            >
              {eligibilityLabel(value)}
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
          {t("reset")}
        </button>
      )}
    </div>
  );
}
