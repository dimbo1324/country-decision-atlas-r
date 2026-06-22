import Link from "next/link";

import { countriesApi } from "../../../shared/api";
import { normalizeLocale } from "../../../shared/lib/locale";
import { routes } from "../../../shared/lib/routes";
import { ErrorState } from "../../../shared/ui/ErrorState";
import {
  CountryHeader,
  CountryCiiBlock,
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
  const locale = normalizeLocale(typeof rawLocale === "string" ? rawLocale : undefined);

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
        <nav className="breadcrumbs" aria-label="Навигация">
          <Link href={routes.countries} className="breadcrumbLink">
            Страны
          </Link>
          <span className="breadcrumbSep" aria-hidden="true">
            /
          </span>
          <span className="breadcrumbCurrent">{slug}</span>
        </nav>
        <header className="pageHeader">
          <p className="eyebrow">Страна</p>
          <h1>{slug}</h1>
        </header>
        <ErrorState
          error={errProp}
          backHref={routes.countries}
          backLabel="Назад к странам"
        />
      </div>
    );
  }

  const isFallback = card.locale.translation_status === "fallback";

  return (
    <div className="pageShell">
      <nav className="breadcrumbs" aria-label="Навигация">
        <Link href={`${routes.countries}?locale=${locale}`} className="breadcrumbLink">
          Страны
        </Link>
        <span className="breadcrumbSep" aria-hidden="true">
          /
        </span>
        <span className="breadcrumbCurrent">{card.country.name}</span>
      </nav>

      {isFallback && (
        <div className="fallbackBanner">
          Русский перевод частично отсутствует. Показана английская fallback-версия.
        </div>
      )}

      <CountryHeader country={card.country} locale={locale} />

      <div className="cardSections" data-testid="country-card">
        {card.profile?.executive_summary && (
          <section className="cardSection cardSectionHighlight">
            <h2 className="cardSectionTitle">Обзор</h2>
            <p className="executiveSummaryText">{card.profile.executive_summary}</p>
          </section>
        )}

        <section className="cardSection" data-testid="cii-section">
          <h2 className="cardSectionTitle">
            Индекс инвестиционной привлекательности (CII)
          </h2>
          <CountryCiiBlock cii={card.cii} />
        </section>

        <section className="cardSection">
          <h2 className="cardSectionTitle">Оценки сценариев</h2>
          <CountryScores scores={card.scores} sources={card.sources} />
        </section>

        <section className="cardSection">
          <h2 className="cardSectionTitle">Профиль страны</h2>
          <CountryProfileSections profile={card.profile} skipExecutiveSummary />
        </section>

        <section className="cardSection">
          <h2 className="cardSectionTitle">Правовые сигналы</h2>
          <p className="cardSectionDesc">
            Правовые сигналы — структурированные изменения и риски, способные повлиять
            на переезд, бизнес, безопасность или долгосрочное планирование.
          </p>
          <CountryLegalSignals legalSignals={card.legal_signals} />
          <div className="entityLinkRow">
            <Link
              href={routes.legalSignalsForCountry(card.country.slug, locale)}
              className="internalLink"
            >
              Все правовые сигналы для {card.country.name} →
            </Link>
          </div>
        </section>

        <section className="cardSection">
          <h2 className="cardSectionTitle">Данные с источниками</h2>
          <CountrySources sources={card.sources} />
          <div className="entityLinkRow">
            <Link
              href={routes.sourcesForCountry(card.country.slug, locale)}
              className="internalLink"
            >
              Все источники для {card.country.name} →
            </Link>
          </div>
        </section>

        <section className="cardSection">
          <h2 className="cardSectionTitle">Доказательства и источники</h2>
          <CountryEvidenceSummary
            evidenceSummary={card.evidence_summary}
            countrySlug={card.country.slug}
            locale={locale}
            sourceSummary={card.profile?.source_summary}
          />
        </section>

        <section className="cardSection">
          <h2 className="cardSectionTitle">Пользовательские истории</h2>
          <CountryUserStoriesSummary userStoriesSummary={card.user_stories_summary} />
        </section>

        <section className="cardSection" data-testid="locale-status">
          <h2 className="cardSectionTitle">Статус перевода</h2>
          <LocaleStatusBadge locale={card.locale} />
        </section>
      </div>
    </div>
  );
}
