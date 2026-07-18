import { getLocale, getTranslations } from "next-intl/server";
import { Kicker } from "@country-decision-atlas/ui";
import { CompareMatrixView } from "../../../features/compare-matrix/CompareMatrixView";

export default async function ComparePage() {
  const locale = await getLocale();
  const t = await getTranslations("comparePage");
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>{t("kicker")}</Kicker>
        <h1 className="font-display text-3xl font-bold">{t("title")}</h1>
        <p className="text-c3 max-w-2xl text-sm leading-relaxed">
          {t("description")}
        </p>
      </header>
      <CompareMatrixView locale={locale} />
    </div>
  );
}
