import { Badge, Card } from "@country-decision-atlas/ui";
import type { GlossaryTerm as GlossaryTermData } from "../../shared/api/glossary";
import { glossaryCategoryLabel } from "../../shared/lib/glossary-labels";
import { useAppLocale } from "../../shared/lib/useAppLocale";
import { RelatedTermChip } from "./RelatedTermChip";

export function GlossaryTermEntry({ term }: { term: GlossaryTermData }) {
  const locale = useAppLocale();
  return (
    <div data-testid="glossary-term-entry">
      <Card
        interactive={false}
        className="flex flex-col gap-3"
      >
        <div className="flex flex-wrap items-center justify-between gap-2">
          <span className="font-display text-lg font-semibold">
            {term.term}
          </span>
          <Badge variant="info">
            {glossaryCategoryLabel(term.category, locale)}
          </Badge>
        </div>
        <p className="text-c3 text-sm leading-relaxed">{term.definition}</p>
        {term.related_terms && term.related_terms.length > 0 && (
          <div className="flex flex-wrap items-center gap-3">
            <span className="font-mono text-c4 text-[9px] tracking-[0.15em] uppercase">
              Связанные термины:
            </span>
            {term.related_terms.map((slug) => (
              <RelatedTermChip
                key={slug}
                slug={slug}
              />
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
