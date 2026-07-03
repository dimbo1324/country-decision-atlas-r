import { AccountView } from "../../features/auth";

export const dynamic = "force-dynamic";

export default function AccountPage() {
  return (
    <div className="pageShell">
      <header className="pageHeader">
        <p className="eyebrow">Личный кабинет</p>
        <h1>Личный кабинет</h1>
      </header>
      <AccountView />
    </div>
  );
}
