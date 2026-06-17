import { apiGet } from "../lib/api";

export const dynamic = "force-dynamic";

type Scenarios = {
  items: Array<{ slug: string; name: string; description?: string | null }>;
};

export default async function ScenariosPage() {
  const scenarios = await apiGet<Scenarios>("/api/v1/scenarios?locale=en");

  return (
    <main className="pageShell">
      <header className="pageHeader">
        <p className="eyebrow">Scenarios</p>
        <h1>Decision scenarios</h1>
      </header>

      {scenarios.ok ? (
        <section className="dataGrid">
          {scenarios.data.items.map((scenario) => (
            <article className="dataCard" key={scenario.slug}>
              <span>{scenario.name}</span>
              <small>{scenario.description ?? scenario.slug}</small>
            </article>
          ))}
        </section>
      ) : (
        <p className="notice">{scenarios.error}</p>
      )}
    </main>
  );
}
