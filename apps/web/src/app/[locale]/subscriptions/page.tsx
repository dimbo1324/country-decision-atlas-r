import { useTranslations } from "next-intl";
import { Kicker } from "@country-decision-atlas/ui";
import { SubscriptionsView } from "../../../features/subscriptions";

export const dynamic = "force-dynamic";

export default function SubscriptionsPage() {
  const t = useTranslations("subscriptionsPage");
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>{t("kicker")}</Kicker>
        <h1 className="font-display text-4xl font-bold">{t("title")}</h1>
        <p className="text-c3 max-w-2xl text-sm leading-relaxed">
          {t("description")}
        </p>
      </header>
      <SubscriptionsView />
    </div>
  );
}
