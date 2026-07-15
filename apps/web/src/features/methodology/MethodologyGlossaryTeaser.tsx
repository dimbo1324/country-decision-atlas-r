import { Kicker } from "@country-decision-atlas/ui";
import { Link } from "../../i18n/navigation";
import { routes } from "../../shared/lib/routes";
import { GlossaryTerm } from "../../shared/ui/GlossaryTerm";
import type { GlossaryTerm as GlossaryTermData } from "../../shared/api/glossary";
import { ArrowNext } from "../../shared/ui/LinkArrow";

export function MethodologyGlossaryTeaser({
  terms,
}: {
  terms: GlossaryTermData[];
}) {
  return (
    <section
      className="flex flex-col gap-4"
      data-testid="glossary-section"
      aria-label="Глоссарий"
    >
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Kicker>Глоссарий терминов</Kicker>
        <Link
          href={routes.glossary}
          className="font-mono text-c3 hover:text-gold3 text-[10px] tracking-[0.2em] uppercase transition-colors duration-300"
        >
          Открыть полный глоссарий <ArrowNext />
        </Link>
      </div>
      <p className="text-c3 max-w-2xl text-sm leading-relaxed">
        Наведите или нажмите на термин, чтобы увидеть его определение.
      </p>
      <div className="flex flex-wrap gap-x-4 gap-y-3">
        {terms.map((term) => (
          <GlossaryTerm
            key={term.slug}
            slug={term.slug}
          >
            {term.term}
          </GlossaryTerm>
        ))}
      </div>
    </section>
  );
}
