"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { normalizeLocale } from "../lib/locale";
import { routes, withLocale } from "../lib/routes";
import { AppNavigation } from "./AppNavigation";
import { LocaleSwitcher } from "./LocaleSwitcher";

export function AppHeader() {
  const searchParams = useSearchParams();
  const locale = normalizeLocale(searchParams.get("locale"));
  return (
    <header className="appHeader">
      <div className="appHeaderInner">
        <Link href={withLocale(routes.home, locale)} className="appTitle">
          Country Decision Atlas
        </Link>
        <AppNavigation />
        <LocaleSwitcher />
      </div>
    </header>
  );
}
