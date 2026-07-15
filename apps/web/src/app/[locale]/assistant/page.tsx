import { getLocale } from "next-intl/server";
import { Kicker } from "@country-decision-atlas/ui";
import { AIAssistantView } from "../../../features/ai-assistant";
import { asSupportedLocale } from "../../../shared/lib/locale";

export const dynamic = "force-dynamic";

export default async function AssistantPage() {
  const locale = asSupportedLocale(await getLocale());

  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>AI-помощник</Kicker>
        <h1 className="font-display text-4xl font-bold">
          Задайте вопрос по опубликованным данным проекта
        </h1>
        <p className="text-c3 max-w-2xl text-sm leading-relaxed">
          Ответ основан только на опубликованных источниках. Если контекста
          недостаточно, помощник откажется отвечать.
        </p>
      </header>
      <AIAssistantView locale={locale} />
    </div>
  );
}
