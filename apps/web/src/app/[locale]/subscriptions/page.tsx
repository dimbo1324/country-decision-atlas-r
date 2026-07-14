import { Kicker } from "@country-decision-atlas/ui";
import { SubscriptionsView } from "../../../features/subscriptions";

export const dynamic = "force-dynamic";

export default function SubscriptionsPage() {
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>Личный кабинет</Kicker>
        <h1 className="font-display text-4xl font-bold">Подписки и лента</h1>
        <p className="text-c3 max-w-2xl text-sm leading-relaxed">
          Следите за метриками и авторами платформы — обновления появляются в
          ленте ниже.
        </p>
      </header>
      <SubscriptionsView />
    </div>
  );
}
