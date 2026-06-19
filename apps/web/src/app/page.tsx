import Link from "next/link";
import { routes } from "../shared/lib/routes";

const ANALYSIS_ITEMS = [
  "Residence and migration",
  "Long-term status and citizenship",
  "Cost of living",
  "Business and self-employment",
  "Safety and political risk",
  "Sources and evidence",
];

export default function Home() {
  return (
    <div className="homePage">
      <section className="homeHero">
        <p className="eyebrow">Country Decision Atlas</p>
        <h1>Compare countries with source-backed intelligence.</h1>
        <p className="heroSubtitle">
          Country Decision Atlas helps compare countries using structured country cards,
          legal signals, scenario scores, and explainable decision results.
        </p>
        <div className="homeActions">
          <Link href={routes.countries} className="homeActionPrimary">
            Explore countries
          </Link>
          <Link href={routes.decision} className="homeActionSecondary">
            Run decision
          </Link>
        </div>
      </section>

      <section className="homeSection">
        <h2 className="homeSectionTitle">MVP: Russia vs Uruguay</h2>
        <p className="homeSectionDesc">
          The current MVP compares two countries across relocation, residence, business,
          safety, and long-term migration scenarios.
        </p>
        <div className="homeCountryCards">
          <div className="homeCountryCard">
            <span className="homeCountryName">Russia</span>
            <span className="homeCountryIso">RU</span>
            <div className="homeCountryLinks">
              <Link href={`${routes.country("russia")}`} className="homeCountryLink">
                View country card
              </Link>
              <Link href={`${routes.decision}?origin=russia`} className="homeCountryLink">
                Run decision
              </Link>
            </div>
          </div>
          <div className="homeCountryCard">
            <span className="homeCountryName">Uruguay</span>
            <span className="homeCountryIso">UY</span>
            <div className="homeCountryLinks">
              <Link href={`${routes.country("uruguay")}`} className="homeCountryLink">
                View country card
              </Link>
              <Link href={`${routes.decision}?origin=uruguay`} className="homeCountryLink">
                Run decision
              </Link>
            </div>
          </div>
        </div>
        <Link href={routes.decision} className="homeCompareLink">
          Run Russia vs Uruguay comparison →
        </Link>
      </section>

      <section className="homeSection">
        <h2 className="homeSectionTitle">What this platform analyses</h2>
        <ul className="homeAnalysisList">
          {ANALYSIS_ITEMS.map((item) => (
            <li key={item} className="homeAnalysisItem">
              {item}
            </li>
          ))}
        </ul>
      </section>

      <section className="homeSection homeTrustSection">
        <h2 className="homeSectionTitle">Source-backed decision making</h2>
        <p className="homeSectionDesc">
          Scores are not shown alone. Every score is connected to a breakdown of
          weighted criteria, legal signals, source documents, and evidence — so you
          can see why a country ranks where it does, not just that it does.
        </p>
        <div className="homeTrustLinks">
          <Link href={routes.legalSignals} className="homeTrustLink">
            Legal signals →
          </Link>
          <Link href={routes.sources} className="homeTrustLink">
            Sources →
          </Link>
        </div>
      </section>
    </div>
  );
}
