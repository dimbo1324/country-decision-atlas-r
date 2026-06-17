import { apiGet } from "../lib/api";

export const dynamic = "force-dynamic";

type CountryList = {
  items: Array<{ slug: string; name: string; region?: string | null }>;
};

export default async function CountriesPage() {
  const countries = await apiGet<CountryList>("/api/v1/countries?locale=en");

  return (
    <main className="pageShell">
      <header className="pageHeader">
        <p className="eyebrow">Countries</p>
        <h1>Decision-ready country cards</h1>
      </header>

      {countries.ok ? (
        <section className="dataGrid">
          {countries.data.items.map((country) => (
            <a
              className="dataCard"
              href={`/countries/${country.slug}`}
              key={country.slug}
            >
              <span>{country.name}</span>
              <small>{country.region ?? "Region pending"}</small>
            </a>
          ))}
        </section>
      ) : (
        <p className="notice">{countries.error}</p>
      )}
    </main>
  );
}
