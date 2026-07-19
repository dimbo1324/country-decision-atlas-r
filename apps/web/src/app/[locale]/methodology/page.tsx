import { Kicker } from "@country-decision-atlas/ui";
import { getLocale, getTranslations } from "next-intl/server";
import { listGlossaryTerms } from "../../../shared/api/glossary";
import { listMethodologySections } from "../../../shared/api/methodology";
import { asSupportedLocale, toApiLocale } from "../../../shared/lib/locale";
import { Link } from "../../../i18n/navigation";
import { routes } from "../../../shared/lib/routes";
import { DisclaimerNotice } from "../../../shared/ui/DisclaimerNotice";
import { MethodologyAccordion } from "../../../features/methodology/MethodologyAccordion";
import { MethodologyGlossaryTeaser } from "../../../features/methodology/MethodologyGlossaryTeaser";
import { ArrowNext } from "../../../shared/ui/LinkArrow";

export const dynamic = "force-dynamic";

export default async function MethodologyPage() {
  const locale = asSupportedLocale(await getLocale());
  const apiLocale = toApiLocale(locale);
  const t = await getTranslations("methodologyPage");

  let sections;
  try {
    const response = await listMethodologySections(apiLocale);
    sections = response.items;
  } catch {
    return (
      <main
        className="flex flex-col gap-6"
        data-testid="methodology-page"
      >
        <header className="flex flex-col gap-3">
          <Kicker>{t("kicker")}</Kicker>
          <h1 className="font-display text-4xl font-bold">{t("title")}</h1>
        </header>
        <p className="text-c3 text-sm">{t("loadError")}</p>
      </main>
    );
  }

  let glossaryTerms: Awaited<ReturnType<typeof listGlossaryTerms>>["items"] =
    [];
  try {
    const glossary = await listGlossaryTerms(apiLocale);
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
        <Kicker>{t("kicker")}</Kicker>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h1 className="font-display text-4xl font-bold">{t("title")}</h1>
          <Link
            href={routes.methodologyParameters}
            className="font-mono text-c3 hover:text-gold3 border-warm border px-4 py-2 text-[10px] tracking-[0.2em] uppercase transition-colors duration-300"
          >
            {t("parametersLink")} <ArrowNext />
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
