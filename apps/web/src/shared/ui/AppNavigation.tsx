"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { routes } from "../lib/routes";

const NAV_ITEMS = [
  { label: "Countries", href: routes.countries },
  { label: "Decision", href: routes.decision },
  { label: "Legal Signals", href: routes.legalSignals },
  { label: "Sources", href: routes.sources },
  { label: "Data Quality", href: routes.dataQuality },
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
