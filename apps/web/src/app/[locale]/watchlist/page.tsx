import { useTranslations } from "next-intl";
import { Kicker } from "@country-decision-atlas/ui";
import { WatchlistView } from "../../../features/watchlist";

export const dynamic = "force-dynamic";

export default function WatchlistPage() {
  const t = useTranslations("watchlistPage");
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>{t("kicker")}</Kicker>
        <h1 className="font-display text-4xl font-bold">{t("title")}</h1>
      </header>
      <WatchlistView />
    </div>
  );
}
