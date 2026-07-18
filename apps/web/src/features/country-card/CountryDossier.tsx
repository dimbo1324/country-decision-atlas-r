"use client";

import type { ReactNode } from "react";
import { useMemo } from "react";
import { parseAsStringEnum, useQueryState } from "nuqs";
import {
  Card,
  DossierRail,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@country-decision-atlas/ui";
import type { components } from "@country-decision-atlas/contracts/generated/types";
import { Link } from "../../i18n/navigation";
import { useFeatureEnabled } from "../../shared/features/FeatureProvider";
import { toApiLocale, type SupportedLocale } from "../../shared/lib/locale";
import { routes } from "../../shared/lib/routes";
import { ArrowNext } from "../../shared/ui/LinkArrow";
import { CommunityCountryBlock } from "../community";
import { CountryDriftBlock } from "../country-drift";
import { CountryDataJournalBlock } from "../data-journal";
import { CountryMigrationBoardBlock } from "../migration-board";
import { PlatformIntelligenceBlock } from "../platform-intelligence";
import { CountryRoutesBlock } from "../routes";
import { TrustSurfaceBlock } from "../trust-surface";
import { CountryWhatChanged } from "../what-changed";
import {
  CountryCiiBlock,
  CountryEvidenceSummary,
  CountryLegalSignals,
  CountryProfileSections,
  CountryScores,
  CountrySources,
  CountryUserStoriesSummary,
  LocaleStatusBadge,
} from "./index";

type CountryReadModelResponse =
  components["schemas"]["CountryReadModelResponse"];

const TAB_IDS = [
  "overview",
  "scores",
  "trust",
  "signals",
  "community",
] as const;
type TabId = (typeof TAB_IDS)[number];

const TAB_LABELS: Record<TabId, string> = {
  overview: "Обзор",
  scores: "Оценки",
  trust: "Доверие",
  signals: "Сигналы",
  community: "Сообщество",
};

// Wide/data-table-heavy sections read better spanning the full tab width
// than sitting in a 2-column grid cell.
const WIDE_SECTION_IDS = new Set([
  "community",
  "migration-board",
  "sources",
  "legal-signals",
]);

interface DossierSectionDef {
  id: string;
  tabId: TabId;
  railLabel: string;
  content: ReactNode;
}

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

interface CountryDossierProps {
  card: CountryReadModelResponse;
  locale: SupportedLocale;
}

/** Renders the country dossier's 17 data sections, either as the existing
 * flat vertical stack (default) or grouped into 5 tabs behind the
 * `web_dossier_v2` flag — same section markup either way, built once here,
 * so the two layouts can never drift out of sync with each other.
 * `DossierRail` gets every section id/label for the flat layout, and only
 * the active tab's subset for the tabbed one. */
export function CountryDossier({ card, locale }: CountryDossierProps) {
  const apiLocale = toApiLocale(locale);
  const isTabbedLayout = useFeatureEnabled("web_dossier_v2");
  const [activeTab, setActiveTab] = useQueryState(
    "tab",
    parseAsStringEnum<TabId>([...TAB_IDS]).withDefault("overview"),
  );

  const sections = useMemo<DossierSectionDef[]>(() => {
    const list: DossierSectionDef[] = [];

    if (card.profile?.executive_summary) {
      list.push({
        id: "overview",
        tabId: "overview",
        railLabel: "Обзор",
        content: (
          <section
            id="overview"
            className="scroll-mt-24"
          >
            <Card
              accent="gold"
              interactive={false}
            >
              <h2 className="font-display mb-3 text-xl font-semibold">Обзор</h2>
              <p className="text-c2 text-sm leading-relaxed">
                {card.profile.executive_summary}
              </p>
            </Card>
          </section>
        ),
      });
    }

    list.push({
      id: "cii",
      tabId: "overview",
      railLabel: "CII",
      content: (
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
      ),
    });

    list.push({
      id: "platform-intelligence",
      tabId: "scores",
      railLabel: "Платформенный интеллект",
      content: (
        <DossierSection
          id="platform-intelligence"
          title="Платформенный интеллект"
          testId="platform-intelligence-section"
        >
          <PlatformIntelligenceBlock
            countrySlug={card.country.slug}
            locale={apiLocale}
          />
        </DossierSection>
      ),
    });

    list.push({
      id: "trust",
      tabId: "trust",
      railLabel: "Доверие",
      content: (
        <DossierSection
          id="trust"
          title="Качество данных"
          testId="trust-surface-section"
        >
          <TrustSurfaceBlock
            countrySlug={card.country.slug}
            locale={apiLocale}
          />
        </DossierSection>
      ),
    });

    list.push({
      id: "drift",
      tabId: "scores",
      railLabel: "Тренды",
      content: (
        <DossierSection
          id="drift"
          title="Направление изменений"
          testId="country-drift-section"
        >
          <CountryDriftBlock
            countrySlug={card.country.slug}
            locale={apiLocale}
          />
        </DossierSection>
      ),
    });

    list.push({
      id: "scores",
      tabId: "scores",
      railLabel: "Скоры",
      content: (
        <DossierSection
          id="scores"
          title="Оценки сценариев"
        >
          <CountryScores
            scores={card.scores}
            sources={card.sources}
          />
        </DossierSection>
      ),
    });

    list.push({
      id: "routes",
      tabId: "signals",
      railLabel: "Маршруты",
      content: (
        <DossierSection
          id="routes"
          title="Маршруты"
        >
          <CountryRoutesBlock
            countrySlug={card.country.slug}
            locale={apiLocale}
          />
        </DossierSection>
      ),
    });

    list.push({
      id: "migration-board",
      tabId: "community",
      railLabel: "Доска переезда",
      content: (
        <DossierSection
          id="migration-board"
          title="Люди, планирующие это направление"
          testId="country-migration-board-section"
        >
          <CountryMigrationBoardBlock countrySlug={card.country.slug} />
        </DossierSection>
      ),
    });

    list.push({
      id: "profile",
      tabId: "overview",
      railLabel: "Профиль",
      content: (
        <DossierSection
          id="profile"
          title="Профиль страны"
        >
          <CountryProfileSections
            profile={card.profile}
            skipExecutiveSummary
          />
        </DossierSection>
      ),
    });

    list.push({
      id: "what-changed",
      tabId: "overview",
      railLabel: "Что изменилось",
      content: (
        <DossierSection
          id="what-changed"
          title="Что изменилось"
          testId="what-changed-section"
        >
          <CountryWhatChanged
            countrySlug={card.country.slug}
            locale={apiLocale}
          />
        </DossierSection>
      ),
    });

    list.push({
      id: "data-journal",
      tabId: "trust",
      railLabel: "Журнал данных",
      content: (
        <DossierSection
          id="data-journal"
          title="Последние обновления данных"
        >
          <CountryDataJournalBlock
            countrySlug={card.country.slug}
            locale={apiLocale}
          />
        </DossierSection>
      ),
    });

    list.push({
      id: "legal-signals",
      tabId: "signals",
      railLabel: "Правовые сигналы",
      content: (
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
            Все правовые сигналы для {card.country.name} <ArrowNext />
          </Link>
        </DossierSection>
      ),
    });

    list.push({
      id: "sources",
      tabId: "trust",
      railLabel: "Источники",
      content: (
        <DossierSection
          id="sources"
          title="Данные с источниками"
        >
          <CountrySources sources={card.sources} />
          <Link
            href={routes.sourcesForCountry(card.country.slug)}
            className="text-gold3 hover:text-gold text-sm transition-colors duration-300"
          >
            Все источники для {card.country.name} <ArrowNext />
          </Link>
        </DossierSection>
      ),
    });

    list.push({
      id: "evidence",
      tabId: "overview",
      railLabel: "Доказательства",
      content: (
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
      ),
    });

    list.push({
      id: "user-stories",
      tabId: "community",
      railLabel: "Истории",
      content: (
        <DossierSection
          id="user-stories"
          title="Пользовательские истории"
        >
          <CountryUserStoriesSummary
            userStoriesSummary={card.user_stories_summary}
          />
        </DossierSection>
      ),
    });

    list.push({
      id: "community",
      tabId: "community",
      railLabel: "Community",
      content: (
        <DossierSection
          id="community"
          title="Community"
          testId="community-section"
        >
          <CommunityCountryBlock countrySlug={card.country.slug} />
        </DossierSection>
      ),
    });

    list.push({
      id: "locale-status",
      tabId: "overview",
      railLabel: "Перевод",
      content: (
        <DossierSection
          id="locale-status"
          title="Статус перевода"
          testId="locale-status"
        >
          <LocaleStatusBadge locale={card.locale} />
        </DossierSection>
      ),
    });

    return list;
  }, [card, locale, apiLocale]);

  if (!isTabbedLayout) {
    return (
      <div className="flex gap-8">
        <div
          className="flex min-w-0 flex-1 flex-col gap-8"
          data-testid="country-card"
        >
          {sections.map((section) => (
            <div key={section.id}>{section.content}</div>
          ))}
        </div>
        <DossierRail
          sections={sections.map(({ id, railLabel }) => ({
            id,
            label: railLabel,
          }))}
        />
      </div>
    );
  }

  const activeSections = sections.filter(
    (section) => section.tabId === activeTab,
  );

  return (
    <div
      className="flex gap-8"
      data-testid="country-dossier-tabs"
    >
      <div
        className="min-w-0 flex-1"
        data-testid="country-card"
      >
        <Tabs
          value={activeTab}
          onValueChange={(value) => void setActiveTab(value as TabId)}
        >
          <TabsList>
            {TAB_IDS.map((tabId) => (
              <TabsTrigger
                key={tabId}
                value={tabId}
                data-testid={`dossier-tab-${tabId}`}
              >
                {TAB_LABELS[tabId]}
              </TabsTrigger>
            ))}
          </TabsList>
          {TAB_IDS.map((tabId) => (
            <TabsContent
              key={tabId}
              value={tabId}
              data-testid={`dossier-tab-panel-${tabId}`}
            >
              <div className="grid gap-6 lg:grid-cols-2">
                {sections
                  .filter((section) => section.tabId === tabId)
                  .map((section) => (
                    <div
                      key={section.id}
                      className={
                        WIDE_SECTION_IDS.has(section.id)
                          ? "lg:col-span-2"
                          : undefined
                      }
                    >
                      {section.content}
                    </div>
                  ))}
              </div>
            </TabsContent>
          ))}
        </Tabs>
      </div>
      <DossierRail
        sections={activeSections.map(({ id, railLabel }) => ({
          id,
          label: railLabel,
        }))}
      />
    </div>
  );
}
