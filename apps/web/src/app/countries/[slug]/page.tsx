import { apiGet } from "../../lib/api";

export const dynamic = "force-dynamic";

type PageProps = {
  params: Promise<{ slug: string }>;
};

type CountryCardResponse = {
  item: {
    executive_summary: string;
    migration_overview: string;
    business_overview: string;
    safety_overview: string;
    risk_summary: string;
    source_summary: string;
  };
};

type ScoreResponse = {
  items: Array<{
    scenario_slug: string;
    scenario_name: string;
    score: number;
    score_label: string;
  }>;
};

export default async function CountryPage({ params }: PageProps) {
  const { slug } = await params;
  const [card, scores] = await Promise.all([
    apiGet<CountryCardResponse>(`/api/v1/countries/${slug}/card?locale=en`),
    apiGet<ScoreResponse>(`/api/v1/countries/${slug}/scores?locale=en`),
  ]);

  return (
    <main className="pageShell">
      <header className="pageHeader">
        <p className="eyebrow">Country card</p>
        <h1>{slug}</h1>
      </header>

      {card.ok ? (
        <section className="detailStack">
          <article className="widePanel">
            <h2>Executive summary</h2>
            <p>{card.data.item.executive_summary}</p>
          </article>
          <div className="twoColumn">
            <article>
              <h2>Migration</h2>
              <p>{card.data.item.migration_overview}</p>
            </article>
            <article>
              <h2>Business</h2>
              <p>{card.data.item.business_overview}</p>
            </article>
            <article>
              <h2>Safety</h2>
              <p>{card.data.item.safety_overview}</p>
            </article>
            <article>
              <h2>Risks</h2>
              <p>{card.data.item.risk_summary}</p>
            </article>
          </div>
          <article className="widePanel">
            <h2>Sources</h2>
            <p>{card.data.item.source_summary}</p>
          </article>
        </section>
      ) : (
        <p className="notice">{card.error}</p>
      )}

      {scores.ok ? (
        <section className="dataGrid">
          {scores.data.items.map((score) => (
            <article className="dataCard" key={score.scenario_slug}>
              <span>{score.scenario_name}</span>
              <strong>{score.score}</strong>
              <small>{score.score_label}</small>
            </article>
          ))}
        </section>
      ) : null}
    </main>
  );
}
