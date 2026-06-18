import { countriesApi } from "../../../shared/api";
import { normalizeLocale } from "../../../shared/lib/locale";
import { ErrorState } from "../../../shared/ui/ErrorState";
import {
  CountryHeader,
  CountryEvidenceSummary,
  CountryLegalSignals,
  CountryProfileSections,
  CountryScores,
  CountrySources,
  CountryUserStoriesSummary,
  LocaleStatusBadge,
} from "../../../features/country-card";

export const dynamic = "force-dynamic";

type PageProps = {
  params: Promise<{ slug: string }>;
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

export default async function CountryPage({ params, searchParams }: PageProps) {
  const { slug } = await params;
  const resolvedSearchParams = await searchParams;
  const rawLocale = resolvedSearchParams["locale"];
  const locale = normalizeLocale(
    typeof rawLocale === "string" ? rawLocale : undefined,
  );

  let card;
  try {
    card = await countriesApi.getCountryCard(slug, locale);
  } catch (err: unknown) {
    const errProp =
      err instanceof Error
        ? err.message
        : (err as { error?: { code?: string; message?: string } });
    return (
      <div className="pageShell">
        <header className="pageHeader">
          <p className="eyebrow">Country</p>
          <h1>{slug}</h1>
        </header>
        <ErrorState error={errProp} />
      </div>
    );
  }

  return (
    <div className="pageShell">
      <CountryHeader country={card.country} />

      <div className="cardSections">
        <section className="cardSection">
          <h2 className="cardSectionTitle">Profile</h2>
          <CountryProfileSections profile={card.profile} />
        </section>

        <section className="cardSection">
          <h2 className="cardSectionTitle">Scores</h2>
          <CountryScores scores={card.scores} />
        </section>

        <section className="cardSection">
          <h2 className="cardSectionTitle">Legal signals</h2>
          <CountryLegalSignals legalSignals={card.legal_signals} />
        </section>

        <section className="cardSection">
          <h2 className="cardSectionTitle">Sources</h2>
          <CountrySources sources={card.sources} />
        </section>

        <section className="cardSection">
          <h2 className="cardSectionTitle">Evidence summary</h2>
          <CountryEvidenceSummary evidenceSummary={card.evidence_summary} />
        </section>

        <section className="cardSection">
          <h2 className="cardSectionTitle">User stories summary</h2>
          <CountryUserStoriesSummary
            userStoriesSummary={card.user_stories_summary}
          />
        </section>

        <section className="cardSection">
          <h2 className="cardSectionTitle">Translation status</h2>
          <LocaleStatusBadge locale={card.locale} />
        </section>
      </div>
    </div>
  );
}
