import { Kicker } from "@country-decision-atlas/ui";
import { TranslationJobsAdminView } from "../../../features/admin-translation-jobs";

export const dynamic = "force-dynamic";

export default function TranslationJobsAdminPage() {
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>Internal</Kicker>
        <h1 className="font-display text-4xl font-bold">Очередь переводов</h1>
      </header>
      <TranslationJobsAdminView />
    </div>
  );
}
