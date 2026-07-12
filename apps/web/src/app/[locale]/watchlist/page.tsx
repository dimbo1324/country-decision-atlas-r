import { WatchlistView } from "../../../features/watchlist";

export const dynamic = "force-dynamic";

export default function WatchlistPage() {
  return (
    <div className="pageShell">
      <header className="pageHeader">
        <p className="eyebrow">Watchlist</p>
        <h1>Мой watchlist</h1>
      </header>
      <WatchlistView />
    </div>
  );
}
