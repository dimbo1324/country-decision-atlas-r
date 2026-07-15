import { getLocale } from "next-intl/server";
import { Card, Kicker } from "@country-decision-atlas/ui";
import { scenariosApi } from "../../../shared/api";
import { asSupportedLocale } from "../../../shared/lib/locale";

export const dynamic = "force-dynamic";

export default async function ScenariosPage() {
  const locale = asSupportedLocale(await getLocale());

  let scenarios;
  try {
    scenarios = await scenariosApi.listScenarios({ locale });
  } catch {
    return (
      <main className="flex flex-col gap-6">
        <header className="flex flex-col gap-3">
          <Kicker>Сценарии</Kicker>
          <h1 className="font-display text-4xl font-bold">
            Сценарии подбора страны
          </h1>
        </header>
        <p className="text-c3 text-sm">Не удалось загрузить сценарии.</p>
      </main>
    );
  }

  return (
    <main className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>Сценарии</Kicker>
        <h1 className="font-display text-4xl font-bold">
          Сценарии подбора страны
        </h1>
      </header>
      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {scenarios.items.map((scenario) => (
          <Card
            interactive={false}
            className="flex flex-col gap-1"
            key={scenario.slug}
          >
            <span className="text-c1 text-sm font-medium">
              {scenario.name}
            </span>
            <small className="text-c3 text-xs">
              {scenario.description ?? scenario.slug}
            </small>
          </Card>
        ))}
      </section>
    </main>
  );
}
