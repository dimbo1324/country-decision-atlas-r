"use client";

import Link from "next/link";
import { usePathname, useSearchParams } from "next/navigation";
import { useAuth } from "../auth/AuthProvider";
import { normalizeLocale } from "../lib/locale";
import { routes, withLocale } from "../lib/routes";

const NAV_ITEMS = [
  { label: "Страны", href: routes.countries },
  { label: "Подбор", href: routes.decision },
  { label: "Правовые сигналы", href: routes.legalSignals },
  { label: "Источники", href: routes.sources },
];

const ADMIN_ROLES = new Set(["editor", "admin", "owner"]);

export function AppNavigation() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const locale = normalizeLocale(searchParams.get("locale"));
  const { user } = useAuth();
  const canSeeDataQuality = user !== null && ADMIN_ROLES.has(user.role);

  return (
    <nav className="appNav">
      {NAV_ITEMS.map((item) => (
        <Link
          key={item.href}
          href={withLocale(item.href, locale)}
          className="navLink"
          data-active={pathname === item.href || pathname.startsWith(item.href + "/")}
        >
          {item.label}
        </Link>
      ))}
      {canSeeDataQuality && (
        <Link
          href={withLocale(routes.dataQuality, locale)}
          className="navLink"
          data-testid="nav-data-quality-link"
          data-active={pathname === routes.dataQuality}
        >
          Качество данных
        </Link>
      )}
    </nav>
  );
}
