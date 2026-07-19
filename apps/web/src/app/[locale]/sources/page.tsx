import { useTranslations } from "next-intl";
import { Kicker } from "@country-decision-atlas/ui";
import { SourcesView } from "../../../features/sources";
import { DisclaimerNotice } from "../../../shared/ui/DisclaimerNotice";

export const dynamic = "force-dynamic";

export default function SourcesPage() {
  const t = useTranslations("sourcesPage");
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>{t("kicker")}</Kicker>
        <h1 className="font-display text-4xl font-bold">{t("title")}</h1>
      </header>
      <SourcesView />
      <DisclaimerNotice />
    </div>
  );
}
