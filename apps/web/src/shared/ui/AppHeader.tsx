import Link from "next/link";
import { routes } from "../lib/routes";
import { AppNavigation } from "./AppNavigation";

export function AppHeader() {
  return (
    <header className="appHeader">
      <div className="appHeaderInner">
        <Link href={routes.home} className="appTitle">
          Country Decision Atlas
        </Link>
        <AppNavigation />
      </div>
    </header>
  );
}
