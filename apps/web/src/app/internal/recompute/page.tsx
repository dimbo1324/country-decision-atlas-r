import { Kicker } from "@country-decision-atlas/ui";
import { RecomputePanelView } from "../../../features/admin-recompute";

export const dynamic = "force-dynamic";

export default function RecomputeAdminPage() {
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>Internal</Kicker>
        <h1 className="font-display text-4xl font-bold">Пересчёт метрик</h1>
      </header>
      <RecomputePanelView />
    </div>
  );
}
