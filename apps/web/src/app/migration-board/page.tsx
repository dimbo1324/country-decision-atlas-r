import { MigrationBoardListView } from "../../features/migration-board";

export const dynamic = "force-dynamic";

export default function MigrationBoardPage() {
  return (
    <div className="pageShell">
      <header className="pageHeader">
        <p className="eyebrow">Migration board</p>
        <h1>Доска переезда</h1>
        <p className="pageLead">
          Найдите людей с похожим направлением переезда без публичного раскрытия
          контактов.
        </p>
      </header>
      <MigrationBoardListView />
    </div>
  );
}
