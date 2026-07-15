import { Kicker } from "@country-decision-atlas/ui";
import { AIDraftsAdminView } from "../../../features/admin-ai-drafts";

export const dynamic = "force-dynamic";

export default function AIDraftsAdminPage() {
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>Internal</Kicker>
        <h1 className="font-display text-4xl font-bold">AI-черновики</h1>
      </header>
      <AIDraftsAdminView />
    </div>
  );
}
