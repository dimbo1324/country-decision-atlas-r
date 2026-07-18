"use client";

import { useMemo, useState } from "react";
import { useTranslations } from "next-intl";
import {
  HorizontalPager,
  MobileStack,
  useMediaQuery,
  useReducedMotion,
  type DeckSlide,
} from "@country-decision-atlas/ui";
import type {
  CountryOverviewCard,
  HomeKeyInsight,
  HomeMatrixPreview as HomeMatrixPreviewData,
  LatestLegalEvent,
  ScenarioWinner,
} from "../../shared/api/home";
import { CountryOverviewCards } from "./CountryOverviewCards";
import { HomeMatrixPreview } from "./HomeMatrixPreview";
import { KeyInsightsPanel } from "./KeyInsightsPanel";
import { LatestLegalEventsPanel } from "./LatestLegalEventsPanel";
import { ScenarioWinnersPanel } from "./ScenarioWinnersPanel";

interface HomeDeckProps {
  countries: CountryOverviewCard[];
  scenarioWinners: ScenarioWinner[];
  matrix: HomeMatrixPreviewData;
  latestLegalEvents: LatestLegalEvent[];
  keyInsights: HomeKeyInsight[];
}

/** Three-zone horizontal deck for the home page's analytical blocks. Desktop
 * (>820px, no reduced-motion preference) pages through the zones via
 * `HorizontalPager`; narrow viewports get `MobileStack`'s native
 * scroll-snap; `prefers-reduced-motion` gets a plain vertical stack with no
 * paging UI at all -- the same flat layout this page used before the deck,
 * so it's also the safest possible fallback.
 *
 * Only one of HorizontalPager/MobileStack is ever mounted (via
 * `useMediaQuery`, not a CSS-only breakpoint toggle) -- mounting both
 * simultaneously and hiding one with CSS would render every panel's content
 * (and its data-testid) twice in the DOM at once. */
export function HomeDeck({
  countries,
  scenarioWinners,
  matrix,
  latestLegalEvents,
  keyInsights,
}: HomeDeckProps) {
  const t = useTranslations("home");
  const [index, setIndex] = useState(0);
  const reducedMotion = useReducedMotion();
  const isDesktop = useMediaQuery("(min-width: 821px)");

  const slides = useMemo<DeckSlide[]>(
    () => [
      {
        id: "countries",
        navLabel: t("slideCountries"),
        accent: "gold",
        content: <CountryOverviewCards countries={countries} />,
      },
      {
        id: "scenarios",
        navLabel: t("slideScenarios"),
        accent: "blue",
        content: (
          <div className="flex flex-col gap-8">
            <ScenarioWinnersPanel winners={scenarioWinners} />
            <HomeMatrixPreview matrix={matrix} />
          </div>
        ),
      },
      {
        id: "signals",
        navLabel: t("slideSignals"),
        accent: "terra",
        content: (
          <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
            <LatestLegalEventsPanel events={latestLegalEvents} />
            <KeyInsightsPanel insights={keyInsights} />
          </div>
        ),
      },
    ],
    [countries, scenarioWinners, matrix, latestLegalEvents, keyInsights, t],
  );

  if (reducedMotion) {
    return (
      <div
        className="flex flex-col gap-16"
        data-testid="home-deck"
      >
        {slides.map((slide) => (
          <div key={slide.id}>{slide.content}</div>
        ))}
      </div>
    );
  }

  return (
    <div
      className="relative h-[640px]"
      data-testid="home-deck"
    >
      {isDesktop ? (
        <HorizontalPager
          slides={slides}
          index={index}
          onIndexChange={setIndex}
          prevLabel={t("pagerPrevLabel")}
          nextLabel={t("pagerNextLabel")}
          prevTooltipPrefix={t("pagerPrevTooltip")}
          nextTooltipPrefix={t("pagerNextTooltip")}
          slidesGroupAriaLabel={t("pagerSlidesGroupLabel")}
        />
      ) : (
        <MobileStack slides={slides} />
      )}
    </div>
  );
}
