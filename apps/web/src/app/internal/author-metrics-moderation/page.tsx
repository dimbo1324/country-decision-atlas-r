import { Kicker } from "@country-decision-atlas/ui";
import { AuthorMetricsModerationView } from "../../../features/author-metrics/AuthorMetricsModerationView";

export const dynamic = "force-dynamic";

export default function AuthorMetricsModerationPage() {
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>Internal</Kicker>
        <h1 className="font-display text-4xl font-bold">
          Модерация авторских метрик
        </h1>
      </header>
      <AuthorMetricsModerationView />
    </div>
  );
}
