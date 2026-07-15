import { Kicker } from "@country-decision-atlas/ui";
import { UsersAdminView } from "../../../features/admin-users";

export const dynamic = "force-dynamic";

export default function UsersAdminPage() {
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>Internal</Kicker>
        <h1 className="font-display text-4xl font-bold">Пользователи</h1>
      </header>
      <UsersAdminView />
    </div>
  );
}
