import { Card } from "@country-decision-atlas/ui";
import { Link } from "../../i18n/navigation";
import type { ScenarioWinner } from "../../shared/api/home";
import { ArrowNext } from "../../shared/ui/LinkArrow";

function formatScore(score: number | null | undefined) {
  return score == null ? "—" : score.toFixed(1);
}

export function ScenarioWinnersPanel({
  winners,
}: {
  winners: ScenarioWinner[];
}) {
  return (
    <section aria-labelledby="home-winners-title">
      <div className="mb-5 flex items-end justify-between gap-4">
        <h2
          id="home-winners-title"
          className="font-display text-2xl font-semibold"
        >
          Победители по сценариям
        </h2>
        <Link
          href="/compare"
          className="font-mono text-c3 hover:text-gold3 text-[10px] tracking-[0.2em] uppercase transition-colors duration-300"
        >
          Открыть матрицу <ArrowNext />
        </Link>
      </div>
      <div
        className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
        data-testid="home-scenario-winners"
      >
        {winners.map((winner) => (
          <Card
            key={winner.scenario_slug}
            interactive={false}
            className="flex flex-col gap-2"
          >
            <h3 className="font-display text-base font-semibold">
              {winner.scenario_name}
            </h3>
            <span className="text-c3 text-sm">
              {winner.winner_country_name ?? "Недостаточно данных"}
            </span>
            <div className="mt-1 flex items-baseline gap-2">
              <b className="font-display text-gold3 text-2xl font-bold">
                {formatScore(winner.winner_score)}
              </b>
              {winner.delta != null && (
                <span className="text-sage3 font-mono text-[10px] tracking-[0.1em]">
                  +{winner.delta.toFixed(1)}
                </span>
              )}
            </div>
          </Card>
        ))}
      </div>
    </section>
  );
}
