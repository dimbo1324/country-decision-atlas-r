import { Kicker } from "@country-decision-atlas/ui";
import { MigrationBoardListView } from "../../../features/migration-board";

export const dynamic = "force-dynamic";

export default function MigrationBoardPage() {
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>Migration board</Kicker>
        <h1 className="font-display text-4xl font-bold">Доска переезда</h1>
        <p className="text-c3 max-w-2xl text-sm leading-relaxed">
          Найдите людей с похожим направлением переезда без публичного раскрытия
          контактов.
        </p>
      </header>
      <MigrationBoardListView />
    </div>
  );
}
