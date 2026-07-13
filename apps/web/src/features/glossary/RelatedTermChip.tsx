"use client";

import { useGlossaryTerm } from "../../shared/glossary/GlossaryProvider";
import { GlossaryTerm } from "../../shared/ui/GlossaryTerm";

export function RelatedTermChip({ slug }: { slug: string }) {
  const term = useGlossaryTerm(slug);
  return <GlossaryTerm slug={slug}>{term?.term ?? slug}</GlossaryTerm>;
}
