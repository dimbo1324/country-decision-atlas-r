import { DataQualityGate } from "../../../features/data-quality";

export const dynamic = "force-dynamic";

export default function DataQualityPage() {
  return (
    <div className="pageShell">
      <header className="pageHeader">
        <p className="eyebrow">Внутреннее</p>
        <h1>Отчёт качества данных</h1>
      </header>
      <DataQualityGate />
    </div>
  );
}
