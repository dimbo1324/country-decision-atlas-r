import Link from "next/link";
import { Suspense } from "react";
import { routes } from "../lib/routes";
import { AppNavigation } from "./AppNavigation";
import { LocaleSwitcher } from "./LocaleSwitcher";

export function AppHeader() {
  return (
    <header className="appHeader">
      <div className="appHeaderInner">
        <Link href={routes.home} className="appTitle">
          Country Decision Atlas
        </Link>
        <AppNavigation />
        <Suspense>
          <LocaleSwitcher />
        </Suspense>
      </div>
    </header>
  );
}
