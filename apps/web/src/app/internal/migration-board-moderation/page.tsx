import { MigrationBoardModerationView } from "../../../features/migration-board";

export const dynamic = "force-dynamic";

export default function MigrationBoardModerationPage() {
  return (
    <div className="pageShell">
      <header className="pageHeader">
        <p className="eyebrow">Internal</p>
        <h1>Модерация доски переезда</h1>
      </header>
      <MigrationBoardModerationView />
    </div>
  );
}
