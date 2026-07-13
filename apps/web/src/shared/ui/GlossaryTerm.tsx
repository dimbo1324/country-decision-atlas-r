"use client";

import type { ReactNode } from "react";
import {
  Badge,
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@country-decision-atlas/ui";
import { useGlossaryTerm } from "../glossary/GlossaryProvider";
import { GLOSSARY_CATEGORY_LABELS } from "../lib/glossary-labels";

type GlossaryTermProps = {
  slug: string;
  children: ReactNode;
};

/** Dotted-underline term reference that opens a definition popover on
 * click. Degrades to plain text if the slug isn't in the loaded glossary —
 * callers never need to guard for a missing term themselves. */
export function GlossaryTerm({ slug, children }: GlossaryTermProps) {
  const term = useGlossaryTerm(slug);

  if (!term) {
    return <>{children}</>;
  }

  return (
    <Popover>
      <PopoverTrigger asChild>
        <button
          type="button"
          data-testid="glossary-term-trigger"
          data-term-slug={slug}
          className="text-c1 hover:text-gold3 hover:border-gold3 border-b border-dotted border-c4 transition-colors duration-300"
        >
          {children}
        </button>
      </PopoverTrigger>
      <PopoverContent data-testid="glossary-term-popover">
        <div className="flex flex-col gap-2">
          <div className="flex items-center justify-between gap-2">
            <span className="font-display text-sm font-semibold">
              {term.term}
            </span>
            <Badge variant="info">
              {GLOSSARY_CATEGORY_LABELS[term.category] ?? term.category}
            </Badge>
          </div>
          <p className="text-c3 text-sm leading-relaxed">{term.definition}</p>
        </div>
      </PopoverContent>
    </Popover>
  );
}
