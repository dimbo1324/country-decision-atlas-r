import { getLocaleFromSearchParams } from "../../shared/lib/locale";
import { scenariosApi } from "../../shared/api";

export const dynamic = "force-dynamic";

type PageProps = {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

export default async function ScenariosPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const locale = getLocaleFromSearchParams(params);

  let scenarios;
  try {
    scenarios = await scenariosApi.listScenarios({ locale });
  } catch {
    return (
      <main className="pageShell">
        <header className="pageHeader">
          <p className="eyebrow">Сценарии</p>
          <h1>Сценарии подбора страны</h1>
        </header>
        <p className="notice">Не удалось загрузить сценарии.</p>
      </main>
    );
  }

  return (
    <main className="pageShell">
      <header className="pageHeader">
        <p className="eyebrow">Сценарии</p>
        <h1>Сценарии подбора страны</h1>
      </header>
      <section className="dataGrid">
        {scenarios.items.map((scenario) => (
          <article className="dataCard" key={scenario.slug}>
            <span>{scenario.name}</span>
            <small>{scenario.description ?? scenario.slug}</small>
          </article>
        ))}
      </section>
    </main>
  );
}
