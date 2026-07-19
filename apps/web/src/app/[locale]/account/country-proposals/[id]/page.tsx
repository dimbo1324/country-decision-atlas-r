import { getTranslations } from "next-intl/server";
import { Kicker } from "@country-decision-atlas/ui";
import { CountryProposalWizardView } from "../../../../../features/country-proposals";

export const dynamic = "force-dynamic";

type PageProps = {
  params: Promise<{ id: string }>;
};

export default async function CountryProposalWizardPage({ params }: PageProps) {
  const { id } = await params;
  const t = await getTranslations("countryProposalWizardPage");
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>{t("kicker")}</Kicker>
        <h1 className="font-display text-4xl font-bold">{t("title")}</h1>
      </header>
      <CountryProposalWizardView proposalId={id} />
    </div>
  );
}
