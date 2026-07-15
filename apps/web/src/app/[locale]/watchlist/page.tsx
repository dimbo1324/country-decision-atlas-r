import { Kicker } from "@country-decision-atlas/ui";
import { WatchlistView } from "../../../features/watchlist";

export const dynamic = "force-dynamic";

export default function WatchlistPage() {
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>Watchlist</Kicker>
        <h1 className="font-display text-4xl font-bold">Мой watchlist</h1>
      </header>
      <WatchlistView />
    </div>
  );
}
