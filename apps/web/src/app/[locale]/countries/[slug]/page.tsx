import type { ReactNode } from "react";
import { getLocale } from "next-intl/server";
import { Card, DossierRail, Kicker } from "@country-decision-atlas/ui";
import { getPathname, Link } from "../../../../i18n/navigation";
import { countriesApi } from "../../../../shared/api";
import { asSupportedLocale } from "../../../../shared/lib/locale";
import { routes } from "../../../../shared/lib/routes";
import { ErrorState } from "../../../../shared/ui/ErrorState";
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
} from "../../../../features/country-card";
import { CommunityCountryBlock } from "../../../../features/community";
import { CountryDriftBlock } from "../../../../features/country-drift";
import { CountryDataJournalBlock } from "../../../../features/data-journal";
import { CountryMigrationBoardBlock } from "../../../../features/migration-board";
import { PlatformIntelligenceBlock } from "../../../../features/platform-intelligence";
import { CountryRoutesBlock } from "../../../../features/routes";
import { TrustSurfaceBlock } from "../../../../features/trust-surface";
import { WatchlistButton } from "../../../../features/watchlist";
import { CountryWhatChanged } from "../../../../features/what-changed";

type PageProps = {
  params: Promise<{ slug: string }>;
};

const RAIL_SECTIONS = [
  { id: "overview", label: "Обзор" },
  { id: "cii", label: "CII" },
  { id: "platform-intelligence", label: "Платформенный интеллект" },
  { id: "trust", label: "Доверие" },
  { id: "drift", label: "Тренды" },
  { id: "scores", label: "Скоры" },
  { id: "routes", label: "Маршруты" },
  { id: "migration-board", label: "Доска переезда" },
  { id: "profile", label: "Профиль" },
  { id: "what-changed", label: "Что изменилось" },
  { id: "data-journal", label: "Журнал данных" },
  { id: "legal-signals", label: "Правовые сигналы" },
  { id: "sources", label: "Источники" },
  { id: "evidence", label: "Доказательства" },
  { id: "user-stories", label: "Истории" },
  { id: "community", label: "Community" },
  { id: "locale-status", label: "Перевод" },
];

function DossierSection({
  id,
  title,
  description,
  testId,
  children,
}: {
  id: string;
  title: string;
  description?: string;
  testId?: string;
  children: ReactNode;
}) {
  return (
    <section
      id={id}
      data-testid={testId}
      className="scroll-mt-24"
    >
      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <h2 className="font-display text-xl font-semibold">{title}</h2>
        {description && (
          <p className="text-c3 text-sm leading-relaxed">{description}</p>
        )}
        {children}
      </Card>
    </section>
  );
}

export default async function CountryPage({ params }: PageProps) {
  const { slug } = await params;
  const locale = asSupportedLocale(await getLocale());

  let card;
  try {
    card = await countriesApi.getCountryCard(slug, locale);
  } catch (err: unknown) {
    const errProp =
      err instanceof Error
        ? err.message
        : (err as { error?: { code?: string; message?: string } });
    return (
      <div className="flex flex-col gap-6">
        <nav
          aria-label="Навигация"
          className="text-c4 flex items-center gap-2 text-xs"
        >
          <Link
            href={routes.countries}
            className="hover:text-gold transition-colors duration-300"
          >
            Страны
          </Link>
          <span aria-hidden="true">/</span>
          <span>{slug}</span>
        </nav>
        <header className="flex flex-col gap-3">
          <Kicker>Страна</Kicker>
          <h1 className="font-display text-3xl font-bold">{slug}</h1>
        </header>
        <ErrorState
          error={errProp}
          backHref={getPathname({ href: routes.countries, locale })}
          backLabel="Назад к странам"
        />
      </div>
    );
  }

  const isFallback = card.locale.translation_status === "fallback";

  return (
    <div className="flex flex-col gap-6">
      <nav
        aria-label="Навигация"
        className="text-c4 flex items-center gap-2 text-xs"
      >
        <Link
          href={routes.countries}
          className="hover:text-gold transition-colors duration-300"
        >
          Страны
        </Link>
        <span aria-hidden="true">/</span>
        <span>{card.country.name}</span>
      </nav>

      {isFallback && (
        <p className="border-terra2/60 text-terra3 border px-4 py-3 text-sm">
          Русский перевод частично отсутствует. Показана английская
          fallback-версия.
        </p>
      )}

      <CountryHeader country={card.country} />

      <div data-testid="watchlist-button-container">
        <WatchlistButton countrySlug={card.country.slug} />
      </div>

      <div className="flex gap-8">
        <div
          className="flex min-w-0 flex-1 flex-col gap-8"
          data-testid="country-card"
        >
          {card.profile?.executive_summary && (
            <section
              id="overview"
              className="scroll-mt-24"
            >
              <Card
                accent="gold"
                interactive={false}
              >
                <h2 className="font-display mb-3 text-xl font-semibold">
                  Обзор
                </h2>
                <p className="text-c2 text-sm leading-relaxed">
                  {card.profile.executive_summary}
                </p>
              </Card>
            </section>
          )}

          <DossierSection
            id="cii"
            title="Индекс инвестиционной привлекательности (CII)"
            testId="cii-section"
          >
            <CountryCiiBlock
              cii={card.cii}
              countrySlug={card.country.slug}
              locale={locale}
            />
          </DossierSection>

          <DossierSection
            id="platform-intelligence"
            title="Платформенный интеллект"
            testId="platform-intelligence-section"
          >
            <PlatformIntelligenceBlock
              countrySlug={card.country.slug}
              locale={locale}
            />
          </DossierSection>

          <DossierSection
            id="trust"
            title="Качество данных"
            testId="trust-surface-section"
          >
            <TrustSurfaceBlock
              countrySlug={card.country.slug}
              locale={locale}
            />
          </DossierSection>

          <DossierSection
            id="drift"
            title="Направление изменений"
            testId="country-drift-section"
          >
            <CountryDriftBlock
              countrySlug={card.country.slug}
              locale={locale}
            />
          </DossierSection>

          <DossierSection
            id="scores"
            title="Оценки сценариев"
          >
            <CountryScores
              scores={card.scores}
              sources={card.sources}
            />
          </DossierSection>

          <DossierSection
            id="routes"
            title="Маршруты"
          >
            <CountryRoutesBlock
              countrySlug={card.country.slug}
              locale={locale}
            />
          </DossierSection>

          <DossierSection
            id="migration-board"
            title="Люди, планирующие это направление"
            testId="country-migration-board-section"
          >
            <CountryMigrationBoardBlock countrySlug={card.country.slug} />
          </DossierSection>

          <DossierSection
            id="profile"
            title="Профиль страны"
          >
            <CountryProfileSections
              profile={card.profile}
              skipExecutiveSummary
            />
          </DossierSection>

          <DossierSection
            id="what-changed"
            title="Что изменилось"
            testId="what-changed-section"
          >
            <CountryWhatChanged
              countrySlug={card.country.slug}
              locale={locale}
            />
          </DossierSection>

          <DossierSection
            id="data-journal"
            title="Последние обновления данных"
          >
            <CountryDataJournalBlock
              countrySlug={card.country.slug}
              locale={locale}
            />
          </DossierSection>

          <DossierSection
            id="legal-signals"
            title="Правовые сигналы"
            description="Правовые сигналы — структурированные изменения и риски, способные повлиять на переезд, бизнес, безопасность или долгосрочное планирование."
          >
            <CountryLegalSignals legalSignals={card.legal_signals} />
            <Link
              href={routes.legalSignalsForCountry(card.country.slug)}
              className="text-gold3 hover:text-gold text-sm transition-colors duration-300"
            >
              Все правовые сигналы для {card.country.name} →
            </Link>
          </DossierSection>

          <DossierSection
            id="sources"
            title="Данные с источниками"
          >
            <CountrySources sources={card.sources} />
            <Link
              href={routes.sourcesForCountry(card.country.slug)}
              className="text-gold3 hover:text-gold text-sm transition-colors duration-300"
            >
              Все источники для {card.country.name} →
            </Link>
          </DossierSection>

          <DossierSection
            id="evidence"
            title="Доказательства и источники"
          >
            <CountryEvidenceSummary
              evidenceSummary={card.evidence_summary}
              countrySlug={card.country.slug}
              sourceSummary={card.profile?.source_summary}
            />
          </DossierSection>

          <DossierSection
            id="user-stories"
            title="Пользовательские истории"
          >
            <CountryUserStoriesSummary
              userStoriesSummary={card.user_stories_summary}
            />
          </DossierSection>

          <DossierSection
            id="community"
            title="Community"
            testId="community-section"
          >
            <CommunityCountryBlock countrySlug={card.country.slug} />
          </DossierSection>

          <DossierSection
            id="locale-status"
            title="Статус перевода"
            testId="locale-status"
          >
            <LocaleStatusBadge locale={card.locale} />
          </DossierSection>
        </div>

        <DossierRail sections={RAIL_SECTIONS} />
      </div>
    </div>
  );
}
