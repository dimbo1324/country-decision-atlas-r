import Link from "next/link";
import type { ScenarioWinner } from "../../shared/api/home";

export function ScenarioWinnersPanel({ winners }: { winners: ScenarioWinner[] }) {
  return (
    <section className="homeOverviewSection" aria-labelledby="home-winners-title">
      <div className="homeSectionHeading">
        <h2 id="home-winners-title">Победители по сценариям</h2>
        <Link href="/compare">Открыть матрицу</Link>
      </div>
      <div className="homeScenarioWinners" data-testid="home-scenario-winners">
        {winners.map((winner) => (
          <article className="homeWinnerRow" key={winner.scenario_slug}>
            <div>
              <h3>{winner.scenario_name}</h3>
              <span>{winner.winner_country_name ?? "Недостаточно данных"}</span>
            </div>
            <div className="homeWinnerScores">
              <strong>{formatScore(winner.winner_score)}</strong>
              {winner.delta != null && <span>+{winner.delta.toFixed(1)}</span>}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function formatScore(score: number | null | undefined) {
  return score == null ? "—" : score.toFixed(1);
}
