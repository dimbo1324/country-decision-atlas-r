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
      className="overflow-x-auto"
      data-testid="compare-matrix"
    >
      <table
        className="w-full border-collapse"
        data-testid="compare-matrix-table"
      >
        <thead>
          <tr>
            <th scope="col" />
            {scenarios.map((s) => (
              <th
                key={s.slug}
                scope="col"
                data-testid="matrix-scenario-header"
                className="font-mono text-c4 border-warm border-b px-3 py-2 text-[8px] font-normal tracking-[0.15em] uppercase"
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
                scope="row"
                className="border-warm border-r px-3 py-2 text-left text-sm font-semibold"
              >
                {country.name}
              </th>
              {scenarios.map((scenario) => {
                const cell = cellMap.get(`${country.slug}::${scenario.slug}`);
                if (!cell) {
                  return (
                    <td
                      key={scenario.slug}
                      className="border-warm text-c4 border p-3 text-center"
                      data-testid="compare-matrix-cell"
                    >
                      —
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
