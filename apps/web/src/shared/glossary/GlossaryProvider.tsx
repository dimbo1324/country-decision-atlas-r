"use client";

import { createContext, useContext, useMemo, type ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { glossaryTermsQuery } from "../../entities/glossary/api";
import { useAppLocale } from "../lib/useAppLocale";
import { toApiLocale } from "../lib/locale";
import type { GlossaryTerm } from "../api/glossary";

type GlossaryContextValue = {
  termsBySlug: Map<string, GlossaryTerm>;
};

const GlossaryContext = createContext<GlossaryContextValue | null>(null);

/** One fetch of the full glossary (the contract has no pagination for this
 * list) covers every `GlossaryTerm` popover mounted anywhere under this
 * provider — mounted once, per locale, in `[locale]/layout.tsx`. */
export function GlossaryProvider({ children }: { children: ReactNode }) {
  const locale = useAppLocale();
  const { data } = useQuery(glossaryTermsQuery(toApiLocale(locale)));

  const termsBySlug = useMemo(
    () => new Map((data?.items ?? []).map((term) => [term.slug, term])),
    [data],
  );

  return (
    <GlossaryContext.Provider value={{ termsBySlug }}>
      {children}
    </GlossaryContext.Provider>
  );
}

export function useGlossaryTerm(slug: string): GlossaryTerm | undefined {
  const context = useContext(GlossaryContext);
  return context?.termsBySlug.get(slug);
}
