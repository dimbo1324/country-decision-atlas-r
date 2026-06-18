import type { CountryReadModelResponse } from "../../shared/api/countries";

type CountryHeaderProps = {
  country: CountryReadModelResponse["country"];
};

export function CountryHeader({ country }: CountryHeaderProps) {
  return (
    <div>
      <header className="pageHeader">
        <p className="eyebrow">{country.region ?? "Country"}</p>
        <h1>{country.name}</h1>
      </header>
      <div className="metaRow">
        {country.iso_code && (
          <span className="metaChip">ISO: {country.iso_code}</span>
        )}
        <span className="metaChip">Status: {country.status}</span>
      </div>
    </div>
  );
}
