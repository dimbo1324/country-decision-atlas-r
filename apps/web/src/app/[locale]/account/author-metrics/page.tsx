import { Kicker } from "@country-decision-atlas/ui";
import { AuthorMetricsStudioView } from "../../../../features/author-metrics";

export const dynamic = "force-dynamic";

export default function AuthorMetricsStudioPage() {
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>Личный кабинет</Kicker>
        <h1 className="font-display text-4xl font-bold">
          Студия авторских метрик
        </h1>
      </header>
      <AuthorMetricsStudioView />
    </div>
  );
}
