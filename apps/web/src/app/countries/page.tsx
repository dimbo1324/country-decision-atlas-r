import Link from "next/link";
import { countriesApi } from "../../shared/api";
import { getLocaleFromSearchParams } from "../../shared/lib/locale";
import { routes } from "../../shared/lib/routes";
import { ErrorState } from "../../shared/ui/ErrorState";

export const dynamic = "force-dynamic";

type PageProps = {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

export default async function CountriesPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const locale = getLocaleFromSearchParams(params);

  let countries;
  try {
    countries = await countriesApi.listCountries({ locale });
  } catch (err) {
    return (
      <div className="pageShell">
        <header className="pageHeader">
          <p className="eyebrow">Countries</p>
          <h1>Decision-ready country cards</h1>
        </header>
        <ErrorState error={err instanceof Error ? err.message : undefined} />
      </div>
    );
  }

  return (
    <div className="pageShell">
      <header className="pageHeader">
        <p className="eyebrow">Countries</p>
        <h1>Decision-ready country cards</h1>
      </header>
      <section className="dataGrid">
        {countries.items.map((country) => (
          <Link
            className="dataCard"
            href={`${routes.country(country.slug)}?locale=${locale}`}
            key={country.slug}
          >
            <span>{country.name}</span>
            <small>{country.region ?? "Region pending"}</small>
          </Link>
        ))}
      </section>
    </div>
  );
}
