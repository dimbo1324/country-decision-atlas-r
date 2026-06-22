import Link from "next/link";
import type { HomeMatrixPreview as HomeMatrixPreviewData } from "../../shared/api/home";

export function HomeMatrixPreview({ matrix }: { matrix: HomeMatrixPreviewData }) {
  const cells = new Map(
    matrix.cells.map((cell) => [`${cell.country_slug}:${cell.scenario_slug}`, cell]),
  );
  return (
    <section className="homeOverviewSection" aria-labelledby="home-matrix-title">
      <div className="homeSectionHeading">
        <div>
          <h2 id="home-matrix-title">Матрица CII</h2>
          <p>Компактный обзор сценарных оценок.</p>
        </div>
        <Link href="/compare">Полная матрица</Link>
      </div>
      <div className="homeMatrixPreview" data-testid="home-matrix-preview">
        {matrix.countries.length === 0 || matrix.scenarios.length === 0 ? (
          <span>Матрица пока недоступна.</span>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Страна</th>
                {matrix.scenarios.map((scenario) => (
                  <th key={scenario.slug}>{scenario.name}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {matrix.countries.map((country) => (
                <tr key={country.slug}>
                  <th>{country.name}</th>
                  {matrix.scenarios.map((scenario) => {
                    const cell = cells.get(`${country.slug}:${scenario.slug}`);
                    return (
                      <td
                        className={matrixClass(cell?.score_label)}
                        key={scenario.slug}
                      >
                        {cell?.score == null ? "—" : cell.score.toFixed(1)}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </section>
  );
}

function matrixClass(label: string | null | undefined) {
  if (label === "excellent" || label === "strong") return "homeMatrixStrong";
  if (label === "moderate") return "homeMatrixModerate";
  if (label === "limited") return "homeMatrixLimited";
  if (label === "weak") return "homeMatrixWeak";
  return "homeMatrixMissing";
}
