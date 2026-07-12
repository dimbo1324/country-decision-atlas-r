import { SearchView } from "../../../features/search";

export const dynamic = "force-dynamic";

export default function SearchPage() {
  return (
    <div className="pageShell">
      <header className="pageHeader">
        <p className="eyebrow">Поиск</p>
        <h1>Поиск по платформе</h1>
      </header>
      <SearchView />
    </div>
  );
}
