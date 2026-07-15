import { Kicker } from "@country-decision-atlas/ui";
import { getLocale } from "next-intl/server";
import { listGlossaryTerms } from "../../../shared/api/glossary";
import { listMethodologySections } from "../../../shared/api/methodology";
import { asSupportedLocale } from "../../../shared/lib/locale";
import { Link } from "../../../i18n/navigation";
import { routes } from "../../../shared/lib/routes";
import { DisclaimerNotice } from "../../../shared/ui/DisclaimerNotice";
import { MethodologyAccordion } from "../../../features/methodology/MethodologyAccordion";
import { MethodologyGlossaryTeaser } from "../../../features/methodology/MethodologyGlossaryTeaser";
import { ArrowNext } from "../../../shared/ui/LinkArrow";

export const dynamic = "force-dynamic";

export default async function MethodologyPage() {
  const locale = asSupportedLocale(await getLocale());

  let sections;
  try {
    const response = await listMethodologySections(locale);
    sections = response.items;
  } catch {
    return (
      <main
        className="flex flex-col gap-6"
        data-testid="methodology-page"
      >
        <header className="flex flex-col gap-3">
          <Kicker>Методология</Kicker>
          <h1 className="font-display text-4xl font-bold">
            Методология платформы
          </h1>
        </header>
        <p className="text-c3 text-sm">Не удалось загрузить методологию.</p>
      </main>
    );
  }

  let glossaryTerms: Awaited<ReturnType<typeof listGlossaryTerms>>["items"] =
    [];
  try {
    const glossary = await listGlossaryTerms(locale);
    glossaryTerms = glossary.items;
  } catch {
    glossaryTerms = [];
  }

  return (
    <main
      className="flex flex-col gap-8"
      data-testid="methodology-page"
    >
      <header className="flex flex-col gap-3">
        <Kicker>Методология</Kicker>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h1 className="font-display text-4xl font-bold">
            Методология платформы
          </h1>
          <Link
            href={routes.methodologyParameters}
            className="font-mono text-c3 hover:text-gold3 border-warm border px-4 py-2 text-[10px] tracking-[0.2em] uppercase transition-colors duration-300"
          >
            Параметры методологии <ArrowNext />
          </Link>
        </div>
      </header>

      <MethodologyAccordion sections={sections} />

      {glossaryTerms.length > 0 && (
        <MethodologyGlossaryTeaser terms={glossaryTerms} />
      )}

      <DisclaimerNotice />
    </main>
  );
}
