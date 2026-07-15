import { cn } from "@country-decision-atlas/ui";
import { Link } from "../../i18n/navigation";
import type { HomeMatrixPreview as HomeMatrixPreviewData } from "../../shared/api/home";
import { ArrowNext } from "../../shared/ui/LinkArrow";

const LABEL_CLASS: Record<string, string> = {
  excellent: "text-sage3",
  strong: "text-sage3",
  moderate: "text-gold3",
  limited: "text-terra3",
  weak: "text-terra3",
};

export function HomeMatrixPreview({
  matrix,
}: {
  matrix: HomeMatrixPreviewData;
}) {
  const countries = matrix.countries ?? [];
  const scenarios = matrix.scenarios ?? [];
  const cells = new Map(
    (matrix.cells ?? []).map((cell) => [
      `${cell.country_slug}:${cell.scenario_slug}`,
      cell,
    ]),
  );

  return (
    <section aria-labelledby="home-matrix-title">
      <div className="mb-5 flex items-end justify-between gap-4">
        <div>
          <h2
            id="home-matrix-title"
            className="font-display text-2xl font-semibold"
          >
            Матрица CII
          </h2>
          <p className="text-c3 text-sm">Компактный обзор сценарных оценок.</p>
        </div>
        <Link
          href="/compare"
          className="font-mono text-c3 hover:text-gold3 text-[10px] tracking-[0.2em] uppercase transition-colors duration-300"
        >
          Полная матрица <ArrowNext />
        </Link>
      </div>
      <div
        className="border-warm bg-bg2 scrollbar-thin overflow-x-auto border"
        data-testid="home-matrix-preview"
      >
        {countries.length === 0 || scenarios.length === 0 ? (
          <p className="text-c3 p-6 text-sm">Матрица пока недоступна.</p>
        ) : (
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="border-warm border-b">
                <th className="text-c3 font-mono px-4 py-3 text-left text-[9px] tracking-[0.15em] uppercase">
                  Страна
                </th>
                {scenarios.map((scenario) => (
                  <th
                    key={scenario.slug}
                    className="text-c3 font-mono px-4 py-3 text-left text-[9px] tracking-[0.15em] uppercase"
                  >
                    {scenario.name}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {countries.map((country) => (
                <tr
                  key={country.slug}
                  className="border-warm border-b last:border-b-0"
                >
                  <th className="font-display px-4 py-3 text-left font-semibold">
                    {country.name}
                  </th>
                  {scenarios.map((scenario) => {
                    const cell = cells.get(`${country.slug}:${scenario.slug}`);
                    return (
                      <td
                        key={scenario.slug}
                        className={cn(
                          "font-mono px-4 py-3 text-sm",
                          LABEL_CLASS[cell?.score_label ?? ""] ?? "text-c4",
                        )}
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
