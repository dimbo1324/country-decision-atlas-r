"use client";

import { Compass } from "lucide-react";
import { Link } from "../../i18n/navigation";
import { SearchBox } from "../../features/search";
import { routes } from "../lib/routes";
import { AppNavigation } from "./AppNavigation";
import { AuthNav } from "./AuthNav";
import { CommandPalette } from "./CommandPalette";
import { LocaleSwitcher } from "./LocaleSwitcher";
import { MobileNav } from "./MobileNav";

export function AppHeader() {
  return (
    <header className="border-warm bg-bg/85 sticky top-0 z-40 border-b backdrop-blur-md">
      <div className="mx-auto flex max-w-[1400px] items-center justify-between gap-4 px-6 py-4">
        <Link
          href={routes.home}
          aria-label="Country Decision Atlas"
          className="flex shrink-0 items-center gap-3"
        >
          <span className="border-gold2 text-gold flex h-8 w-8 items-center justify-center border">
            <Compass
              width={16}
              height={16}
              strokeWidth={1.5}
            />
          </span>
          <span className="font-display text-shimmer hidden text-sm font-bold tracking-[0.3em] uppercase lg:inline">
            Country Decision Atlas
          </span>
        </Link>

        <AppNavigation className="hidden md:flex" />

        <div className="flex shrink-0 items-center gap-3">
          <SearchBox className="hidden xl:flex" />
          <CommandPalette />
          <AuthNav className="hidden md:flex" />
          <LocaleSwitcher />
          <MobileNav />
        </div>
      </div>
    </header>
  );
}
