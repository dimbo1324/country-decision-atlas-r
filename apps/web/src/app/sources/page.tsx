import { SourcesView } from "../../features/sources";

export const dynamic = "force-dynamic";

export default function SourcesPage() {
  return (
    <div className="pageShell">
      <header className="pageHeader">
        <p className="eyebrow">Sources</p>
        <h1>Evidence sources</h1>
      </header>
      <SourcesView />
    </div>
  );
}
