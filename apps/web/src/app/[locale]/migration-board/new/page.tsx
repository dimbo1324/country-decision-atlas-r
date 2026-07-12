import { MigrationBoardFormView } from "../../../../features/migration-board";

export const dynamic = "force-dynamic";

export default function NewMigrationBoardPostPage() {
  return (
    <div className="pageShell">
      <header className="pageHeader">
        <p className="eyebrow">Новая запись</p>
        <h1>Запланировать переезд</h1>
      </header>
      <MigrationBoardFormView />
    </div>
  );
}
