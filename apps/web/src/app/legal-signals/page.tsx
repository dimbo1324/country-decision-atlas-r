import { LegalSignalsView } from "../../features/legal-signals";

export const dynamic = "force-dynamic";

export default function LegalSignalsPage() {
  return (
    <div className="pageShell">
      <header className="pageHeader">
        <p className="eyebrow">Legal signals</p>
        <h1>Traceable decision signals</h1>
      </header>
      <LegalSignalsView />
    </div>
  );
}
