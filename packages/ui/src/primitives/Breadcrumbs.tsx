"use client";

import type { ReactNode } from "react";
import { ChevronRight } from "lucide-react";
import { cn } from "../lib/cn";

export interface BreadcrumbItem {
  label: string;
  href?: string;
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[];
  /** Render each item's link — pass the app router's `Link` (Next) or a
   * plain anchor; keeps this primitive framework-agnostic. */
  renderLink?: (item: BreadcrumbItem, children: ReactNode) => ReactNode;
  className?: string;
}

export function Breadcrumbs({ items, renderLink, className }: BreadcrumbsProps) {
  return (
    <nav
      aria-label="Хлебные крошки"
      className={cn(
        "font-mono text-c3 flex flex-wrap items-center gap-2 text-[10px] tracking-[0.15em] uppercase",
        className,
      )}
    >
      {items.map((item, index) => {
        const isLast = index === items.length - 1;
        const label = isLast || !item.href ? (
          <span
            className={isLast ? "text-c1" : undefined}
            aria-current={isLast ? "page" : undefined}
          >
            {item.label}
          </span>
        ) : (
          renderLink?.(
            item,
            <span className="hover:text-c1 transition-colors duration-200">
              {item.label}
            </span>,
          ) ?? <span>{item.label}</span>
        );
        return (
          <span
            key={`${item.label}-${index}`}
            className="flex items-center gap-2"
          >
            {label}
            {!isLast && (
              <ChevronRight
                width={11}
                height={11}
                strokeWidth={1.5}
                className="text-c4"
              />
            )}
          </span>
        );
      })}
    </nav>
  );
}
