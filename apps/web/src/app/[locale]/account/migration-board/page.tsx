import { Kicker } from "@country-decision-atlas/ui";
import { AccountMigrationBoardView } from "../../../../features/migration-board";

export const dynamic = "force-dynamic";

export default function AccountMigrationBoardPage() {
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>Личный кабинет</Kicker>
        <h1 className="font-display text-4xl font-bold">Моя доска переезда</h1>
      </header>
      <AccountMigrationBoardView />
    </div>
  );
}
