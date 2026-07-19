"use client";

import { Compass } from "lucide-react";
import { Link } from "../../i18n/navigation";
import { routes } from "../lib/routes";
import { AppNavigation } from "./AppNavigation";
import { AuthNav } from "./AuthNav";
import { CommandPalette } from "./CommandPalette";
import { LocaleSwitcher } from "./LocaleSwitcher";
import { MobileNav } from "./MobileNav";

/** Breakpoints are budgeted against measured widths so the bar never
 * exceeds its container (max-w minus padding = 1352px) for any role or
 * locale: brand text from xl, section nav from lg; the quick-jump trigger
 * and locale switcher are both fixed-width regardless of breakpoint or
 * locale (search itself lives in the ⌘K palette, not a separate box). */
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
          <span className="font-display text-shimmer hidden text-sm font-bold tracking-[0.3em] uppercase xl:inline">
            Country Decision Atlas
          </span>
        </Link>

        <AppNavigation className="hidden lg:flex" />

        <div className="flex shrink-0 items-center gap-3">
          <CommandPalette />
          <LocaleSwitcher />
          <AuthNav
            variant="menu"
            className="hidden lg:flex"
          />
          <MobileNav />
        </div>
      </div>
    </header>
  );
}
