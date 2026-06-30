import { getLocaleFromSearchParams } from "../../shared/lib/locale";
import { listGlossaryTerms } from "../../shared/api/glossary";
import { listMethodologySections } from "../../shared/api/methodology";
import { DisclaimerNotice } from "../../shared/ui/DisclaimerNotice";

export const dynamic = "force-dynamic";

type PageProps = {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

export default async function MethodologyPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const locale = getLocaleFromSearchParams(params);

  let sections;
  let glossaryItems: Awaited<ReturnType<typeof listGlossaryTerms>>["items"] = [];
  try {
    const response = await listMethodologySections(locale);
    sections = response.items;
  } catch {
    return (
      <main className="pageShell">
        <header className="pageHeader">
          <p className="eyebrow">Методология</p>
          <h1>Методология платформы</h1>
        </header>
        <p className="notice">Не удалось загрузить методологию.</p>
      </main>
    );
  }
  try {
    const glossary = await listGlossaryTerms(locale);
    glossaryItems = glossary.items;
  } catch {
    glossaryItems = [];
  }

  return (
    <main className="pageShell" data-testid="methodology-page">
      <header className="pageHeader">
        <p className="eyebrow">Методология</p>
        <h1>Методология платформы</h1>
      </header>
      <section className="methodologySections">
        {sections.map((section) => (
          <article
            className="methodologySection"
            key={section.slug}
            data-section-type={section.section_type}
          >
            <h2 className="methodologySectionTitle">{section.title}</h2>
            {section.summary && (
              <p className="methodologySectionSummary">{section.summary}</p>
            )}
            {section.body && (
              <div className="methodologySectionBody">{section.body}</div>
            )}
          </article>
        ))}
      </section>
      {glossaryItems.length > 0 && (
        <section
          className="methodologySections"
          data-testid="glossary-section"
          aria-label="Глоссарий"
        >
          <h2 className="pageSubheader">Глоссарий терминов</h2>
          {glossaryItems.map((term) => (
            <article
              className="methodologySection"
              key={term.slug}
              data-term-slug={term.slug}
            >
              <h3 className="methodologySectionTitle">{term.term}</h3>
              <p>{term.definition}</p>
              {term.related_terms && term.related_terms.length > 0 && (
                <p className="relatedTerms">
                  Связанные термины: {term.related_terms.join(", ")}
                </p>
              )}
            </article>
          ))}
        </section>
      )}
      <DisclaimerNotice />
    </main>
  );
}
