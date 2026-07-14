import { Kicker } from "@country-decision-atlas/ui";
import { MigrationBoardModerationView } from "../../../features/migration-board";

export const dynamic = "force-dynamic";

export default function MigrationBoardModerationPage() {
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>Internal</Kicker>
        <h1 className="font-display text-4xl font-bold">
          Модерация доски переезда
        </h1>
      </header>
      <MigrationBoardModerationView />
    </div>
  );
}
