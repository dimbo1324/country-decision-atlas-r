import { Kicker } from "@country-decision-atlas/ui";
import { EvidenceAdminView } from "../../../features/admin-evidence";

export const dynamic = "force-dynamic";

export default function EvidenceAdminPage() {
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>Internal</Kicker>
        <h1 className="font-display text-4xl font-bold">
          Источники и правовые сигналы
        </h1>
      </header>
      <EvidenceAdminView />
    </div>
  );
}
