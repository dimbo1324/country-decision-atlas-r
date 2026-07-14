import { Kicker } from "@country-decision-atlas/ui";
import { CountryProposalWizardView } from "../../../../../features/country-proposals";

export const dynamic = "force-dynamic";

type PageProps = {
  params: Promise<{ id: string }>;
};

export default async function CountryProposalWizardPage({ params }: PageProps) {
  const { id } = await params;
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>Заявка страны</Kicker>
        <h1 className="font-display text-4xl font-bold">
          Мастер заявки страны
        </h1>
      </header>
      <CountryProposalWizardView proposalId={id} />
    </div>
  );
}
