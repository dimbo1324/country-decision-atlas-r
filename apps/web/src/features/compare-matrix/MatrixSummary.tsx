import { useTranslations } from "next-intl";
import type {
  MatrixCell,
  MatrixCountry,
  MatrixScenario,
} from "../../shared/api/cii";

type Props = {
  countries: MatrixCountry[];
  scenarios: MatrixScenario[];
  cells: MatrixCell[];
};

function bestCountryForScenario(
  scenario: MatrixScenario,
  countries: MatrixCountry[],
  cells: MatrixCell[],
): MatrixCountry | null {
  let best: MatrixCountry | null = null;
  let bestScore = -Infinity;
  for (const country of countries) {
    const cell = cells.find(
      (c) =>
        c.country_slug === country.slug && c.scenario_slug === scenario.slug,
    );
    if (cell?.cii_score != null && cell.cii_score > bestScore) {
      bestScore = cell.cii_score;
      best = country;
    }
  }
  return best;
}

function bestScenarioForCountry(
  country: MatrixCountry,
  scenarios: MatrixScenario[],
  cells: MatrixCell[],
): MatrixScenario | null {
  let best: MatrixScenario | null = null;
  let bestScore = -Infinity;
  for (const scenario of scenarios) {
    const cell = cells.find(
      (c) =>
        c.country_slug === country.slug && c.scenario_slug === scenario.slug,
    );
    if (cell?.cii_score != null && cell.cii_score > bestScore) {
      bestScore = cell.cii_score;
      best = scenario;
    }
  }
  return best;
}

export function MatrixSummary({ countries, scenarios, cells }: Props) {
  const t = useTranslations("compareMatrix");
  if (countries.length === 0 || scenarios.length === 0) return null;

  const scenarioWinners = scenarios.map((s) => ({
    scenario: s,
    winner: bestCountryForScenario(s, countries, cells),
  }));

  const countryBest = countries.map((c) => ({
    country: c,
    best: bestScenarioForCountry(c, scenarios, cells),
  }));

  return (
    <div
      className="grid grid-cols-1 gap-6 sm:grid-cols-2"
      data-testid="compare-matrix-summary"
    >
      <div className="flex flex-col gap-2">
        <h4 className="font-mono text-c4 text-[9px] tracking-[0.2em] uppercase">
          {t("bestCountryPerScenario")}
        </h4>
        <ul className="text-c3 flex flex-col gap-1 text-sm">
          {scenarioWinners.map(({ scenario, winner }) => (
            <li key={scenario.slug}>
              <span className="text-c4">{scenario.name}:</span>{" "}
              <span className="text-c1 font-semibold">
                {winner?.name ?? "—"}
              </span>
            </li>
          ))}
        </ul>
      </div>
      <div className="flex flex-col gap-2">
        <h4 className="font-mono text-c4 text-[9px] tracking-[0.2em] uppercase">
          {t("bestScenarioPerCountry")}
        </h4>
        <ul className="text-c3 flex flex-col gap-1 text-sm">
          {countryBest.map(({ country, best }) => (
            <li key={country.slug}>
              <span className="text-c4">{country.name}:</span>{" "}
              <span className="text-c1 font-semibold">{best?.name ?? "—"}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
