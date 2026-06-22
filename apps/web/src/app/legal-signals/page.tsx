import { LegalSignalsTimelineView } from "../../features/legal-signals-timeline";

export const dynamic = "force-dynamic";

export default function LegalSignalsPage() {
  return (
    <div className="pageShell">
      <header className="pageHeader">
        <p className="eyebrow">Правовые сигналы</p>
        <h1>Лента правовых сигналов</h1>
      </header>
      <LegalSignalsTimelineView />
    </div>
  );
}
