import Link from "next/link";

import { countriesApi } from "../../../shared/api";
import { normalizeLocale } from "../../../shared/lib/locale";
import { routes } from "../../../shared/lib/routes";
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
        <nav className="breadcrumbs" aria-label="Breadcrumb">
          <Link href={routes.countries} className="breadcrumbLink">
            Countries
          </Link>
          <span className="breadcrumbSep" aria-hidden="true">/</span>
          <span className="breadcrumbCurrent">{slug}</span>
        </nav>
        <header className="pageHeader">
          <p className="eyebrow">Country</p>
          <h1>{slug}</h1>
        </header>
        <ErrorState error={errProp} backHref={routes.countries} backLabel="Back to countries" />
      </div>
    );
  }

  const isFallback = card.locale.translation_status === "fallback";

  return (
    <div className="pageShell">
      <nav className="breadcrumbs" aria-label="Breadcrumb">
        <Link href={`${routes.countries}?locale=${locale}`} className="breadcrumbLink">
          Countries
        </Link>
        <span className="breadcrumbSep" aria-hidden="true">/</span>
        <span className="breadcrumbCurrent">{card.country.name}</span>
      </nav>

      {isFallback && (
        <div className="fallbackBanner">
          {locale === "ru"
            ? "Русский перевод частично отсутствует. Показана английская fallback-версия."
            : "Translation content is missing. Showing fallback language content."}
        </div>
      )}

      <CountryHeader country={card.country} locale={locale} />

      <div className="cardSections">
        {card.profile?.executive_summary && (
          <section className="cardSection cardSectionHighlight">
            <h2 className="cardSectionTitle">Overview</h2>
            <p className="executiveSummaryText">{card.profile.executive_summary}</p>
          </section>
        )}

        <section className="cardSection">
          <h2 className="cardSectionTitle">Scenario scores</h2>
          <CountryScores scores={card.scores} />
        </section>

        <section className="cardSection">
          <h2 className="cardSectionTitle">Country profile</h2>
          <CountryProfileSections profile={card.profile} skipExecutiveSummary />
        </section>

        <section className="cardSection">
          <h2 className="cardSectionTitle">Legal signals</h2>
          <p className="cardSectionDesc">
            Legal signals are structured changes or risks that may affect relocation,
            business, safety, or long-term planning.
          </p>
          <CountryLegalSignals legalSignals={card.legal_signals} />
          <div className="entityLinkRow">
            <Link
              href={routes.legalSignalsForCountry(card.country.slug, locale)}
              className="internalLink"
            >
              View all legal signals for {card.country.name} →
            </Link>
          </div>
        </section>

        <section className="cardSection">
          <h2 className="cardSectionTitle">Source-backed data</h2>
          <CountrySources sources={card.sources} />
          <div className="entityLinkRow">
            <Link
              href={routes.sourcesForCountry(card.country.slug, locale)}
              className="internalLink"
            >
              View all sources for {card.country.name} →
            </Link>
          </div>
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
