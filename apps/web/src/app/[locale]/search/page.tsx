import { useTranslations } from "next-intl";
import { Kicker } from "@country-decision-atlas/ui";
import { SearchView } from "../../../features/search";

export const dynamic = "force-dynamic";

export default function SearchPage() {
  const t = useTranslations("searchPage");
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>{t("kicker")}</Kicker>
        <h1 className="font-display text-4xl font-bold">{t("title")}</h1>
      </header>
      <SearchView />
    </div>
  );
}
