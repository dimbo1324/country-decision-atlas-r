import { getTranslations } from "next-intl/server";
import { Kicker } from "@country-decision-atlas/ui";
import { CountryProposalListView } from "../../../../features/country-proposals";

export const dynamic = "force-dynamic";

export default async function CountryProposalsPage() {
  const t = await getTranslations("countryProposalsPage");
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>{t("kicker")}</Kicker>
        <h1 className="font-display text-4xl font-bold">{t("title")}</h1>
      </header>
      <CountryProposalListView />
    </div>
  );
}
