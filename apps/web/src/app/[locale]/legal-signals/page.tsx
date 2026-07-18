import { Kicker } from "@country-decision-atlas/ui";
import { LegalSignalsRegistryView } from "../../../features/legal-signals-timeline";
import { DisclaimerNotice } from "../../../shared/ui/DisclaimerNotice";

export const dynamic = "force-dynamic";

export default function LegalSignalsPage() {
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>Правовые сигналы</Kicker>
        <h1 className="font-display text-4xl font-bold">
          Лента правовых сигналов
        </h1>
      </header>
      <LegalSignalsRegistryView />
      <DisclaimerNotice />
    </div>
  );
}
