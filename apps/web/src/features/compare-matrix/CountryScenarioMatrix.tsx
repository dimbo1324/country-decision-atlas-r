import type {
  MatrixCell as MatrixCellType,
  MatrixCountry,
  MatrixScenario,
} from "../../shared/api/cii";
import { MatrixCell } from "./MatrixCell";

type Props = {
  countries: MatrixCountry[];
  scenarios: MatrixScenario[];
  cells: MatrixCellType[];
  locale: string;
};

export function CountryScenarioMatrix({
  countries,
  scenarios,
  cells,
  locale,
}: Props) {
  const cellMap = new Map<string, MatrixCellType>();
  for (const cell of cells) {
    cellMap.set(`${cell.country_slug}::${cell.scenario_slug}`, cell);
  }

  return (
    <div
      className="matrixTableWrapper"
      data-testid="compare-matrix"
    >
      <table
        className="matrixTable"
        data-testid="compare-matrix-table"
      >
        <thead>
          <tr>
            <th
              className="matrixCornerCell"
              scope="col"
            />
            {scenarios.map((s) => (
              <th
                key={s.slug}
                className="matrixScenarioHeader"
                scope="col"
              >
                {s.name}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {countries.map((country) => (
            <tr
              key={country.slug}
              data-testid={`matrix-row-${country.slug}`}
            >
              <th
                className="matrixCountryHeader"
                scope="row"
              >
                {country.name}
              </th>
              {scenarios.map((scenario) => {
                const cell = cellMap.get(`${country.slug}::${scenario.slug}`);
                if (!cell) {
                  return (
                    <td
                      key={scenario.slug}
                      className="matrixCell matrixCellMissing"
                      data-testid="compare-matrix-cell"
                    >
                      <span className="matrixCellScore">—</span>
                    </td>
                  );
                }
                return (
                  <MatrixCell
                    key={scenario.slug}
                    cell={cell}
                    locale={locale}
                  />
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
