import { Kicker } from "@country-decision-atlas/ui";
import { UserStoriesView } from "../../../features/user-stories";

export const dynamic = "force-dynamic";

export default function UserStoriesPage() {
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>Сообщество</Kicker>
        <h1 className="font-display text-4xl font-bold">Истории переезда</h1>
        <p className="text-c3 max-w-2xl text-sm leading-relaxed">
          Личный опыт участников сообщества — отделён от проверенных источников
          и публикуется после модерации.
        </p>
      </header>
      <UserStoriesView />
    </div>
  );
}
