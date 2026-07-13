import { Kicker } from "@country-decision-atlas/ui";
import { LegalSignalsTimelineView } from "../../../features/legal-signals-timeline";
import { Link } from "../../../i18n/navigation";
import { routes } from "../../../shared/lib/routes";
import { DisclaimerNotice } from "../../../shared/ui/DisclaimerNotice";

export const dynamic = "force-dynamic";

export default function LegalSignalsPage() {
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>Правовые сигналы</Kicker>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h1 className="font-display text-4xl font-bold">
            Лента правовых сигналов
          </h1>
          <Link
            href={routes.legalSignalsTimeline}
            className="font-mono text-c3 hover:text-gold3 border-warm border px-4 py-2 text-[10px] tracking-[0.2em] uppercase transition-colors duration-300"
          >
            Таймлайн-график →
          </Link>
        </div>
      </header>
      <LegalSignalsTimelineView />
      <DisclaimerNotice />
    </div>
  );
}
