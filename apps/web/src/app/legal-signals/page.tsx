import { LegalSignalsView } from "../../features/legal-signals";

export const dynamic = "force-dynamic";

export default function LegalSignalsPage() {
  return (
    <div className="pageShell">
      <header className="pageHeader">
        <p className="eyebrow">Правовые сигналы</p>
        <h1>Отслеживаемые правовые сигналы</h1>
      </header>
      <LegalSignalsView />
    </div>
  );
}
