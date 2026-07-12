import { Link } from "../../i18n/navigation";
import type { CountryReadModelResponse } from "../../shared/api/countries";
import { routes } from "../../shared/lib/routes";
import { LocalizationBadge } from "../../shared/ui/LocalizationBadge";

type CountryHeaderProps = {
  country: CountryReadModelResponse["country"];
};

export function CountryHeader({ country }: CountryHeaderProps) {
  return (
    <div className="countryHeaderBlock">
      <header className="pageHeader">
        <p className="eyebrow">{country.region ?? "Страна"}</p>
        <h1>{country.name}</h1>
        <div className="metaRow">
          {country.iso_code && (
            <span className="metaChip">ISO: {country.iso_code}</span>
          )}
          <span className="metaChip">Статус: {country.status}</span>
          <LocalizationBadge localization={country.localization} />
        </div>
      </header>
      <div className="quickActions">
        <Link
          href={routes.countries}
          className="quickAction"
        >
          ← Все страны
        </Link>
        <Link
          href={routes.decision}
          className="quickAction quickActionPrimary"
        >
          Запустить подбор
        </Link>
        <Link
          href={routes.legalSignals}
          className="quickAction"
        >
          Правовые сигналы
        </Link>
        <Link
          href={routes.sources}
          className="quickAction"
        >
          Источники
        </Link>
      </div>
    </div>
  );
}
