import { Kicker } from "@country-decision-atlas/ui";
import { MigrationBoardFormView } from "../../../../features/migration-board";

export const dynamic = "force-dynamic";

export default function NewMigrationBoardPostPage() {
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>Новая запись</Kicker>
        <h1 className="font-display text-4xl font-bold">
          Запланировать переезд
        </h1>
      </header>
      <MigrationBoardFormView />
    </div>
  );
}
