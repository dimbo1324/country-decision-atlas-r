import Link from "next/link";
import type { CountryReadModelResponse } from "../../shared/api/countries";
import { routes } from "../../shared/lib/routes";

type CountryHeaderProps = {
  country: CountryReadModelResponse["country"];
  locale?: string;
};

export function CountryHeader({ country, locale = "en" }: CountryHeaderProps) {
  const localeParam = `?locale=${locale}`;

  return (
    <div className="countryHeaderBlock">
      <header className="pageHeader">
        <p className="eyebrow">{country.region ?? "Country"}</p>
        <h1>{country.name}</h1>
        <div className="metaRow">
          {country.iso_code && (
            <span className="metaChip">ISO: {country.iso_code}</span>
          )}
          <span className="metaChip">Status: {country.status}</span>
        </div>
      </header>
      <div className="quickActions">
        <Link href={`${routes.countries}${localeParam}`} className="quickAction">
          ← All countries
        </Link>
        <Link href={`${routes.decision}${localeParam}`} className="quickAction quickActionPrimary">
          Run decision
        </Link>
        <Link href={`${routes.legalSignals}${localeParam}`} className="quickAction">
          Legal signals
        </Link>
        <Link href={`${routes.sources}${localeParam}`} className="quickAction">
          Sources
        </Link>
      </div>
    </div>
  );
}
