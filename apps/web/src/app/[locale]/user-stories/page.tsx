import { getTranslations } from "next-intl/server";
import { Kicker } from "@country-decision-atlas/ui";
import { UserStoriesView } from "../../../features/user-stories";

export const dynamic = "force-dynamic";

export default async function UserStoriesPage() {
  const t = await getTranslations("userStoriesPage");
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>{t("kicker")}</Kicker>
        <h1 className="font-display text-4xl font-bold">{t("title")}</h1>
        <p className="text-c3 max-w-2xl text-sm leading-relaxed">
          {t("description")}
        </p>
      </header>
      <UserStoriesView />
    </div>
  );
}
