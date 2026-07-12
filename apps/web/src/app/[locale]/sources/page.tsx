import { SourcesView } from "../../../features/sources";

export const dynamic = "force-dynamic";

export default function SourcesPage() {
  return (
    <div className="pageShell">
      <header className="pageHeader">
        <p className="eyebrow">Источники</p>
        <h1>Источники доказательств</h1>
      </header>
      <SourcesView />
    </div>
  );
}
