"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { routes } from "../lib/routes";

const NAV_ITEMS = [
  { label: "Страны", href: routes.countries },
  { label: "Подбор", href: routes.decision },
  { label: "Правовые сигналы", href: routes.legalSignals },
  { label: "Источники", href: routes.sources },
  { label: "Качество данных", href: routes.dataQuality },
];

export function AppNavigation() {
  const pathname = usePathname();

  return (
    <nav className="appNav">
      {NAV_ITEMS.map((item) => (
        <Link
          key={item.href}
          href={item.href}
          className="navLink"
          data-active={pathname === item.href || pathname.startsWith(item.href + "/")}
        >
          {item.label}
        </Link>
      ))}
    </nav>
  );
}
