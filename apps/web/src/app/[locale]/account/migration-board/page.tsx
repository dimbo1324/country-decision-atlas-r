import { getTranslations } from "next-intl/server";
import { Kicker } from "@country-decision-atlas/ui";
import { AccountMigrationBoardView } from "../../../../features/migration-board";

export const dynamic = "force-dynamic";

export default async function AccountMigrationBoardPage() {
  const t = await getTranslations("accountMigrationBoardPage");
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>{t("kicker")}</Kicker>
        <h1 className="font-display text-4xl font-bold">{t("title")}</h1>
      </header>
      <AccountMigrationBoardView />
    </div>
  );
}
