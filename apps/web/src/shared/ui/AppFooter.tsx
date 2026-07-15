import { useTranslations } from "next-intl";
import { Link } from "../../i18n/navigation";
import { routes } from "../lib/routes";
import { DisclaimerNotice } from "./DisclaimerNotice";

interface FooterLink {
  labelKey: string;
  descriptionKey: string;
  href: string;
}

interface FooterGroup {
  titleKey: string;
  links: FooterLink[];
}

/** Footer as a descriptive site map: every major section with a one-line
 * "what you'll find there", so orientation never depends on the top bar
 * alone. */
const FOOTER_GROUPS: FooterGroup[] = [
  {
    titleKey: "groupAnalytics",
    links: [
      {
        labelKey: "linkCountries",
        descriptionKey: "descCountries",
        href: routes.countries,
      },
      {
        labelKey: "linkDecision",
        descriptionKey: "descDecision",
        href: routes.decision,
      },
      {
        labelKey: "linkCompare",
        descriptionKey: "descCompare",
        href: routes.compare,
      },
      {
        labelKey: "linkLegalSignals",
        descriptionKey: "descLegalSignals",
        href: routes.legalSignals,
      },
      {
        labelKey: "linkSources",
        descriptionKey: "descSources",
        href: routes.sources,
      },
    ],
  },
  {
    titleKey: "groupKnowledge",
    links: [
      {
        labelKey: "linkMethodology",
        descriptionKey: "descMethodology",
        href: routes.methodology,
      },
      {
        labelKey: "linkGlossary",
        descriptionKey: "descGlossary",
        href: routes.glossary,
      },
      {
        labelKey: "linkScenarios",
        descriptionKey: "descScenarios",
        href: routes.scenarios,
      },
      {
        labelKey: "linkAssistant",
        descriptionKey: "descAssistant",
        href: routes.assistant,
      },
    ],
  },
  {
    titleKey: "groupCommunity",
    links: [
      {
        labelKey: "linkMigrationBoard",
        descriptionKey: "descMigrationBoard",
        href: routes.migrationBoard,
      },
      {
        labelKey: "linkUserStories",
        descriptionKey: "descUserStories",
        href: routes.userStories,
      },
      {
        labelKey: "linkWatchlist",
        descriptionKey: "descWatchlist",
        href: routes.watchlist,
      },
      {
        labelKey: "linkTrips",
        descriptionKey: "descTrips",
        href: routes.trips,
      },
    ],
  },
];

export function AppFooter() {
  const t = useTranslations("footer");

  return (
    <footer className="border-warm mt-auto border-t">
      <nav
        aria-label={t("siteMapLabel")}
        className="border-warm mx-auto grid max-w-[1400px] grid-cols-1 gap-8 border-b px-6 py-10 sm:grid-cols-2 lg:grid-cols-3"
        data-testid="footer-site-map"
      >
        {FOOTER_GROUPS.map((group) => (
          <div
            key={group.titleKey}
            className="flex flex-col gap-3"
          >
            <span className="font-mono text-c4 text-[9px] tracking-[0.25em] uppercase">
              {t(group.titleKey)}
            </span>
            <ul className="flex flex-col gap-2.5">
              {group.links.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="group flex flex-col gap-0.5"
                  >
                    <span className="font-mono text-c2 group-hover:text-gold3 text-[11px] tracking-[0.14em] uppercase transition-colors duration-300">
                      {t(link.labelKey)}
                    </span>
                    <span className="text-c3 text-xs leading-relaxed">
                      {t(link.descriptionKey)}
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </nav>
      <div className="mx-auto flex max-w-[1400px] flex-col gap-4 px-6 py-6 sm:flex-row sm:items-center sm:justify-between">
        <DisclaimerNotice text={t("disclaimer")} />
        <span className="font-mono text-c4 shrink-0 text-[9px] tracking-[0.2em] uppercase">
          {t("refLabel")} · CDA-WEB
        </span>
      </div>
    </footer>
  );
}
