import { Kicker } from "@country-decision-atlas/ui";
import { DataQualityGate } from "../../../features/data-quality";

export const dynamic = "force-dynamic";

export default function DataQualityPage() {
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>Внутреннее</Kicker>
        <h1 className="font-display text-4xl font-bold">
          Отчёт качества данных
        </h1>
      </header>
      <DataQualityGate />
    </div>
  );
}
