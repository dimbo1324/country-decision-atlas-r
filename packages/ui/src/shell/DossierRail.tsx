"use client";

import { useEffect, useRef, useState } from "react";
import { cn } from "../lib/cn";

export interface DossierRailSection {
  id: string;
  label: string;
}

interface DossierRailProps {
  sections: DossierRailSection[];
  className?: string;
  /** This package has no i18n context of its own (Storybook renders it
   * with none at all) — callers with a real locale pass the translated
   * string; untranslated callers keep the original Russian default. */
  ariaLabel?: string;
}

/** Sticky section nav for long single-page dossiers (country card, decision
 * passport). Highlights the section currently intersecting the viewport
 * instead of tracking scroll position by hand — one IntersectionObserver,
 * torn down on unmount. */
export function DossierRail({
  sections,
  className,
  ariaLabel = "Разделы досье",
}: DossierRailProps) {
  const [activeId, setActiveId] = useState(sections[0]?.id ?? "");
  const observerRef = useRef<IntersectionObserver | null>(null);

  useEffect(() => {
    const elements = sections
      .map((section) => document.getElementById(section.id))
      .filter((el): el is HTMLElement => el !== null);
    if (elements.length === 0) return;

    observerRef.current = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
        if (visible[0]) setActiveId(visible[0].target.id);
      },
      { rootMargin: "-15% 0px -70% 0px", threshold: 0 },
    );

    elements.forEach((el) => observerRef.current?.observe(el));
    return () => observerRef.current?.disconnect();
  }, [sections]);

  return (
    <nav
      aria-label={ariaLabel}
      data-testid="dossier-rail"
      className={cn(
        "border-warm bg-bg2/60 sticky top-24 hidden max-h-[calc(100vh-8rem)] w-52 shrink-0 flex-col gap-1 overflow-y-auto border-l px-4 py-2 lg:flex",
        className,
      )}
    >
      {sections.map((section) => (
        <a
          key={section.id}
          href={`#${section.id}`}
          data-testid={`dossier-rail-link-${section.id}`}
          className={cn(
            "font-mono border-l py-1.5 pl-3 text-[10px] tracking-[0.15em] uppercase transition-colors duration-300",
            activeId === section.id
              ? "border-gold text-gold"
              : "border-transparent text-c4 hover:text-c2",
          )}
        >
          {section.label}
        </a>
      ))}
    </nav>
  );
}
