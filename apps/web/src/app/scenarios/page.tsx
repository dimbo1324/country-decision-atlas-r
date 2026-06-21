import { getLocaleFromSearchParams } from "../../shared/lib/locale";
import { apiGet } from "../lib/api";

export const dynamic = "force-dynamic";

type Scenarios = {
  items: Array<{ slug: string; name: string; description?: string | null }>;
};

type PageProps = {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

export default async function ScenariosPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const locale = getLocaleFromSearchParams(params);
  const scenarios = await apiGet<Scenarios>(`/api/v1/scenarios?locale=${locale}`);

  return (
    <main className="pageShell">
      <header className="pageHeader">
        <p className="eyebrow">Сценарии</p>
        <h1>Сценарии подбора страны</h1>
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
