import { Kicker } from "@country-decision-atlas/ui";
import { CountryProposalListView } from "../../../../features/country-proposals";

export const dynamic = "force-dynamic";

export default function CountryProposalsPage() {
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>Личный кабинет</Kicker>
        <h1 className="font-display text-4xl font-bold">Студия заявок стран</h1>
      </header>
      <CountryProposalListView />
    </div>
  );
}
