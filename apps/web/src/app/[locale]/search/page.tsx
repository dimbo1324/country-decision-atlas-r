import { Kicker } from "@country-decision-atlas/ui";
import { SearchView } from "../../../features/search";

export const dynamic = "force-dynamic";

export default function SearchPage() {
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>Поиск</Kicker>
        <h1 className="font-display text-4xl font-bold">Поиск по платформе</h1>
      </header>
      <SearchView />
    </div>
  );
}
