import { Kicker } from "@country-decision-atlas/ui";
import { LegalSignalsChartView } from "../../../../features/legal-signals-chart";
import { DisclaimerNotice } from "../../../../shared/ui/DisclaimerNotice";

export const dynamic = "force-dynamic";

export default function LegalSignalsTimelinePage() {
  return (
    <div
      className="flex flex-col gap-6"
      data-testid="legal-signals-timeline-page"
    >
      <header className="flex flex-col gap-3">
        <Kicker>Правовые сигналы · таймлайн</Kicker>
        <h1 className="font-display text-4xl font-bold">
          Хронология правовых сигналов
        </h1>
      </header>
      <LegalSignalsChartView />
      <DisclaimerNotice />
    </div>
  );
}
