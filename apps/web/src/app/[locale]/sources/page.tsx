import { Kicker } from "@country-decision-atlas/ui";
import { SourcesView } from "../../../features/sources";
import { DisclaimerNotice } from "../../../shared/ui/DisclaimerNotice";

export const dynamic = "force-dynamic";

export default function SourcesPage() {
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>Источники</Kicker>
        <h1 className="font-display text-4xl font-bold">
          Источники доказательств
        </h1>
      </header>
      <SourcesView />
      <DisclaimerNotice />
    </div>
  );
}
