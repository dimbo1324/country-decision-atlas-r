import { Kicker } from "@country-decision-atlas/ui";
import { CommunityModerationView } from "../../../features/community";

export const dynamic = "force-dynamic";

export default function CommunityModerationPage() {
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>Internal</Kicker>
        <h1 className="font-display text-4xl font-bold">
          Модерация сообщества
        </h1>
      </header>
      <CommunityModerationView />
    </div>
  );
}
