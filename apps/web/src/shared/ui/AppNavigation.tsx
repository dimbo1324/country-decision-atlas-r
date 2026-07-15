"use client";

import { cn } from "@country-decision-atlas/ui";
import { useTranslations } from "next-intl";
import { Link, usePathname } from "../../i18n/navigation";
import { routes } from "../lib/routes";

interface AppNavigationProps {
  className?: string;
  onNavigate?: () => void;
}

/** Public sections only; signed-in and role-gated links live in AuthNav
 * so the top bar keeps a bounded width for every role. */
export function AppNavigation({ className, onNavigate }: AppNavigationProps) {
  const t = useTranslations("nav");
  const pathname = usePathname();

  const navItems = [
    { label: t("countries"), href: routes.countries },
    { label: t("decision"), href: routes.decision },
    { label: t("migrationBoard"), href: routes.migrationBoard },
    { label: t("userStories"), href: routes.userStories },
    { label: t("legalSignals"), href: routes.legalSignals },
    { label: t("sources"), href: routes.sources },
  ];

  return (
    <nav
      data-testid="app-nav"
      className={cn("flex items-center gap-6", className)}
    >
      {navItems.map((item) => {
        const isActive =
          pathname === item.href || pathname.startsWith(`${item.href}/`);
        return (
          <Link
            key={item.href}
            href={item.href}
            onClick={onNavigate}
            data-active={isActive}
            className="font-mono text-c3 hover:text-c1 data-[active=true]:text-c1 relative py-1.5 text-[11px] tracking-[0.14em] uppercase transition-colors duration-300"
          >
            {item.label}
            <span
              className={cn(
                "bg-gold absolute inset-x-0 -bottom-0.5 h-px origin-left transition-transform duration-300",
                isActive ? "scale-x-100" : "scale-x-0",
              )}
            />
          </Link>
        );
      })}
    </nav>
  );
}
