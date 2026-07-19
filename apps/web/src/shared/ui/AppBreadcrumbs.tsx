"use client";

import { useTranslations } from "next-intl";
import { Breadcrumbs, type BreadcrumbItem } from "@country-decision-atlas/ui";
import { Link } from "../../i18n/navigation";

type AppBreadcrumbsProps = {
  items: BreadcrumbItem[];
  className?: string;
};

/** Thin client wrapper: `Breadcrumbs`' `renderLink` is a function prop,
 * which can't cross the Server → Client Component boundary (RSC
 * serialization), so async Server Component pages can't pass it directly.
 * This component owns the `renderLink` closure instead and only takes
 * plain serializable `items` from its (possibly server) caller. */
export function AppBreadcrumbs({ items, className }: AppBreadcrumbsProps) {
  const t = useTranslations("breadcrumbs");
  return (
    <Breadcrumbs
      items={items}
      className={className}
      ariaLabel={t("ariaLabel")}
      renderLink={(item, children) => (
        <Link href={item.href ?? "#"}>{children}</Link>
      )}
    />
  );
}
