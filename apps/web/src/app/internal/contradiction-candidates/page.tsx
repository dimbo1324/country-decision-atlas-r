import { Kicker } from "@country-decision-atlas/ui";
import { ContradictionCandidatesAdminView } from "../../../features/admin-contradiction-candidates";

export const dynamic = "force-dynamic";

export default function ContradictionCandidatesAdminPage() {
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>Internal</Kicker>
        <h1 className="font-display text-4xl font-bold">
          Кандидаты на противоречие
        </h1>
      </header>
      <ContradictionCandidatesAdminView />
    </div>
  );
}
