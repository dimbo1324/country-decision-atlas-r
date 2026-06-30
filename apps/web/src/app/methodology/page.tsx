import { getLocaleFromSearchParams } from "../../shared/lib/locale";
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
      <DisclaimerNotice />
    </main>
  );
}
