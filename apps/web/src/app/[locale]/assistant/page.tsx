import { getLocale } from "next-intl/server";
import { AIAssistantView } from "../../../features/ai-assistant";
import { asSupportedLocale } from "../../../shared/lib/locale";

export const dynamic = "force-dynamic";

export default async function AssistantPage() {
  const locale = asSupportedLocale(await getLocale());

  return (
    <div className="pageShell">
      <header className="pageHeader">
        <p className="eyebrow">AI-помощник</p>
        <h1>Задайте вопрос по опубликованным данным проекта</h1>
        <p className="pageSubtitle">
          Ответ основан только на опубликованных источниках. Если контекста
          недостаточно, помощник откажется отвечать.
        </p>
      </header>
      <AIAssistantView locale={locale} />
    </div>
  );
}
