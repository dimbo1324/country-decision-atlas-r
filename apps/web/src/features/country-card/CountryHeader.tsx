import { Badge, Kicker } from "@country-decision-atlas/ui";
import { Link } from "../../i18n/navigation";
import type { CountryReadModelResponse } from "../../shared/api/countries";
import { routes } from "../../shared/lib/routes";
import { LocalizationBadge } from "../../shared/ui/LocalizationBadge";

type CountryHeaderProps = {
  country: CountryReadModelResponse["country"];
};

export function CountryHeader({ country }: CountryHeaderProps) {
  return (
    <div className="flex flex-col gap-5">
      <header className="flex flex-col gap-3">
        <Kicker>{country.region ?? "Страна"}</Kicker>
        <h1 className="font-display text-4xl font-bold">{country.name}</h1>
        <div className="flex flex-wrap items-center gap-2">
          {country.iso_code && (
            <Badge variant="default">ISO: {country.iso_code}</Badge>
          )}
          <Badge variant="default">Статус: {country.status}</Badge>
          <LocalizationBadge localization={country.localization} />
        </div>
      </header>
      <div className="flex flex-wrap gap-4">
        <Link
          href={routes.countries}
          className="font-mono text-c3 hover:text-gold text-[10px] tracking-[0.15em] uppercase transition-colors duration-300"
        >
          ← Все страны
        </Link>
        <Link
          href={routes.decision}
          className="font-mono text-gold3 hover:text-gold text-[10px] tracking-[0.15em] uppercase transition-colors duration-300"
        >
          Запустить подбор
        </Link>
        <Link
          href={routes.legalSignals}
          className="font-mono text-c3 hover:text-gold text-[10px] tracking-[0.15em] uppercase transition-colors duration-300"
        >
          Правовые сигналы
        </Link>
        <Link
          href={routes.sources}
          className="font-mono text-c3 hover:text-gold text-[10px] tracking-[0.15em] uppercase transition-colors duration-300"
        >
          Источники
        </Link>
      </div>
    </div>
  );
}
