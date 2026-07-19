import { useTranslations } from "next-intl";
import {
  GLOSSARY_CATEGORIES,
  glossaryCategoryLabel,
} from "../../shared/lib/glossary-labels";
import { useAppLocale } from "../../shared/lib/useAppLocale";

const SELECT_CLASS =
  "border-warm bg-bg2 text-c1 font-body border px-3 py-2 text-sm transition-colors duration-300 hover:border-[var(--color-c3)] focus:outline-none";
const LABEL_CLASS =
  "font-mono text-c3 flex flex-col gap-1.5 text-[9px] tracking-[0.15em] uppercase";

export function GlossaryFilters({
  q,
  category,
  onQueryChange,
  onCategoryChange,
}: {
  q: string;
  category: string;
  onQueryChange: (value: string) => void;
  onCategoryChange: (value: string) => void;
}) {
  const locale = useAppLocale();
  const t = useTranslations("glossaryFilters");
  return (
    <div
      className="border-warm flex flex-wrap items-end gap-4 border p-4"
      data-testid="glossary-filters"
    >
      <label className={LABEL_CLASS}>
        {t("searchLabel")}
        <input
          type="search"
          className={SELECT_CLASS}
          value={q}
          placeholder={t("searchPlaceholder")}
          onChange={(event) => onQueryChange(event.target.value)}
          data-testid="glossary-search-input"
        />
      </label>
      <label className={LABEL_CLASS}>
        {t("categoryLabel")}
        <select
          className={SELECT_CLASS}
          value={category}
          onChange={(event) => onCategoryChange(event.target.value)}
          data-testid="glossary-category-select"
        >
          <option value="">{t("allCategories")}</option>
          {GLOSSARY_CATEGORIES.map((value) => (
            <option
              key={value}
              value={value}
            >
              {glossaryCategoryLabel(value, locale)}
            </option>
          ))}
        </select>
      </label>
    </div>
  );
}
