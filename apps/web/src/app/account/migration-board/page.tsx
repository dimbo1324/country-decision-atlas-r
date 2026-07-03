import { AccountMigrationBoardView } from "../../../features/migration-board";

export const dynamic = "force-dynamic";

export default function AccountMigrationBoardPage() {
  return (
    <div className="pageShell">
      <header className="pageHeader">
        <p className="eyebrow">Личный кабинет</p>
        <h1>Моя доска переезда</h1>
      </header>
      <AccountMigrationBoardView />
    </div>
  );
}
