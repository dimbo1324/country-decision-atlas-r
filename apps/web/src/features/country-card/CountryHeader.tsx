import Link from "next/link";
import type { CountryReadModelResponse } from "../../shared/api/countries";
import { routes } from "../../shared/lib/routes";
import { LocalizationBadge } from "../../shared/ui/LocalizationBadge";

type CountryHeaderProps = {
  country: CountryReadModelResponse["country"];
  locale?: string;
};

export function CountryHeader({ country, locale = "ru" }: CountryHeaderProps) {
  const localeParam = `?locale=${locale}`;

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
        <Link href={`${routes.countries}${localeParam}`} className="quickAction">
          ← Все страны
        </Link>
        <Link
          href={`${routes.decision}${localeParam}`}
          className="quickAction quickActionPrimary"
        >
          Запустить подбор
        </Link>
        <Link href={`${routes.legalSignals}${localeParam}`} className="quickAction">
          Правовые сигналы
        </Link>
        <Link href={`${routes.sources}${localeParam}`} className="quickAction">
          Источники
        </Link>
      </div>
    </div>
  );
}
