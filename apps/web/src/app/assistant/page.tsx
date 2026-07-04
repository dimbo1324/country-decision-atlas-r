import { AIAssistantView } from "../../features/ai-assistant";
import { normalizeLocale } from "../../shared/lib/locale";

export const dynamic = "force-dynamic";

type PageProps = {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

export default async function AssistantPage({ searchParams }: PageProps) {
  const resolvedSearchParams = await searchParams;
  const rawLocale = resolvedSearchParams["locale"];
  const locale = normalizeLocale(
    typeof rawLocale === "string" ? rawLocale : undefined,
  );

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
