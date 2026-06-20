import { apiPost } from "../lib/api";

export const dynamic = "force-dynamic";

type CompareResult = {
  scenario: { title: string };
  countries: Array<{
    country_slug: string;
    score: number;
    explanation: string;
  }>;
  recommended_country: string | null;
  recommendation_type: string;
  explanation: string;
  caveat: string;
};

export default async function ComparePage() {
  const result = await apiPost<
    CompareResult,
    { scenario_slug: string; country_slugs: string[]; locale: string }
  >("/api/v1/decision/compare", {
    scenario_slug: "relocation_residence",
    country_slugs: ["russia", "uruguay"],
    locale: "ru",
  });

  return (
    <main className="pageShell">
      <header className="pageHeader">
        <p className="eyebrow">Сравнение</p>
        <h1>Россия vs Уругвай</h1>
      </header>

      {result.ok ? (
        <section className="detailStack">
          <article className="widePanel">
            <h2>{result.data.scenario.title}</h2>
            <p>{result.data.explanation}</p>
            <strong>
              {result.data.recommended_country ?? result.data.recommendation_type}
            </strong>
          </article>
          <section className="dataGrid">
            {result.data.countries.map((country) => (
              <article className="dataCard" key={country.country_slug}>
                <span>{country.country_slug}</span>
                <strong>{country.score}</strong>
                <small>{country.explanation}</small>
              </article>
            ))}
          </section>
          <p className="notice">{result.data.caveat}</p>
        </section>
      ) : (
        <p className="notice">{result.error}</p>
      )}
    </main>
  );
}
