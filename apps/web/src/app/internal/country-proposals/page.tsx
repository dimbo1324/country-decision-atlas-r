import { Kicker } from "@country-decision-atlas/ui";
import { CountryProposalsAdminView } from "../../../features/admin-country-proposals";

export const dynamic = "force-dynamic";

export default function CountryProposalsAdminPage() {
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>Internal</Kicker>
        <h1 className="font-display text-4xl font-bold">
          Кураторство заявок стран
        </h1>
      </header>
      <CountryProposalsAdminView />
    </div>
  );
}
