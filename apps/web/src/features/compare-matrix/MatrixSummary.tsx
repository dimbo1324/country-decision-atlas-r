import type { MatrixCell, MatrixCountry, MatrixScenario } from "../../shared/api/cii";

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
      (c) => c.country_slug === country.slug && c.scenario_slug === scenario.slug,
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
      (c) => c.country_slug === country.slug && c.scenario_slug === scenario.slug,
    );
    if (cell?.cii_score != null && cell.cii_score > bestScore) {
      bestScore = cell.cii_score;
      best = scenario;
    }
  }
  return best;
}

export function MatrixSummary({ countries, scenarios, cells }: Props) {
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
    <div className="matrixSummary" data-testid="compare-matrix-summary">
      <h3 className="matrixSummaryTitle">Сводка</h3>
      <div className="matrixSummarySection">
        <h4 className="matrixSummarySectionTitle">Лучшая страна по сценарию</h4>
        <ul className="matrixSummaryList">
          {scenarioWinners.map(({ scenario, winner }) => (
            <li key={scenario.slug} className="matrixSummaryItem">
              <span className="matrixSummaryScenario">{scenario.name}:</span>{" "}
              <span className="matrixSummaryValue">{winner?.name ?? "—"}</span>
            </li>
          ))}
        </ul>
      </div>
      <div className="matrixSummarySection">
        <h4 className="matrixSummarySectionTitle">Лучший сценарий по стране</h4>
        <ul className="matrixSummaryList">
          {countryBest.map(({ country, best }) => (
            <li key={country.slug} className="matrixSummaryItem">
              <span className="matrixSummaryScenario">{country.name}:</span>{" "}
              <span className="matrixSummaryValue">{best?.name ?? "—"}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
