"use client";

import { cn } from "@country-decision-atlas/ui";
import { useTranslations } from "next-intl";
import NextLink from "next/link";
import { Link, usePathname } from "../../i18n/navigation";
import { useAuth } from "../auth/AuthProvider";
import { ADMIN_ROLES, MODERATION_ROLES, hasRole } from "../auth/roles";
import { routes } from "../lib/routes";

interface AppNavigationProps {
  className?: string;
  onNavigate?: () => void;
}

export function AppNavigation({ className, onNavigate }: AppNavigationProps) {
  const t = useTranslations("nav");
  const pathname = usePathname();
  const { user } = useAuth();

  const navItems = [
    { label: t("countries"), href: routes.countries },
    { label: t("decision"), href: routes.decision },
    { label: t("migrationBoard"), href: routes.migrationBoard },
    { label: t("legalSignals"), href: routes.legalSignals },
    { label: t("sources"), href: routes.sources },
  ];

  const canSeeDataQuality = hasRole(user, ADMIN_ROLES);
  const canSeeMigrationBoardModeration = hasRole(user, MODERATION_ROLES);

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
      {canSeeDataQuality && (
        // Plain next/link: /internal/** is deliberately outside the
        // [locale] tree (Stage 12's own shell), so it must never be
        // locale-prefixed.
        <NextLink
          href={routes.dataQuality}
          onClick={onNavigate}
          data-testid="nav-data-quality-link"
          data-active={pathname === routes.dataQuality}
          className="font-mono text-c3 hover:text-c1 data-[active=true]:text-c1 text-[11px] tracking-[0.14em] uppercase transition-colors duration-300"
        >
          {t("dataQuality")}
        </NextLink>
      )}
      {canSeeMigrationBoardModeration && (
        <NextLink
          href={routes.migrationBoardModeration}
          onClick={onNavigate}
          data-testid="nav-migration-board-moderation-link"
          data-active={pathname === routes.migrationBoardModeration}
          className="font-mono text-c3 hover:text-c1 data-[active=true]:text-c1 text-[11px] tracking-[0.14em] uppercase transition-colors duration-300"
        >
          {t("moderation")}
        </NextLink>
      )}
    </nav>
  );
}
