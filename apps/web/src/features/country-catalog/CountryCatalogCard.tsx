import { Card } from "@country-decision-atlas/ui";
import { Link } from "../../i18n/navigation";
import type { components } from "@country-decision-atlas/contracts/generated/types";
import { flagEmoji } from "../../shared/lib/flagEmoji";
import { routes } from "../../shared/lib/routes";
import { WatchlistStar } from "./WatchlistStar";
import { ArrowNext } from "../../shared/ui/LinkArrow";

type Country = components["schemas"]["Country"];

export function CountryCatalogCard({
  country,
  saved,
  authenticated,
}: {
  country: Country;
  saved: boolean;
  authenticated: boolean;
}) {
  return (
    <Card className="relative flex flex-col gap-4">
      <div className="absolute top-4 right-4">
        <WatchlistStar
          countrySlug={country.slug}
          countryName={country.name}
          saved={saved}
          authenticated={authenticated}
        />
      </div>
      <Link
        href={routes.country(country.slug)}
        className="flex flex-1 flex-col gap-4"
      >
        <div className="flex items-center gap-3 pr-10">
          <span
            className="text-3xl leading-none"
            aria-hidden
          >
            {flagEmoji(country.iso2) || "—"}
          </span>
          <div className="min-w-0">
            <h3 className="font-display truncate text-lg leading-snug font-semibold">
              {country.name}
            </h3>
            <span className="font-mono text-c4 text-[9px] tracking-[0.2em] uppercase">
              {country.iso2}
            </span>
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          {country.region && (
            <span className="border-warm text-c3 font-mono border px-2 py-1 text-[9px] tracking-[0.1em] uppercase">
              {country.region}
            </span>
          )}
          {country.subregion && (
            <span className="border-warm text-c4 font-mono border px-2 py-1 text-[9px] tracking-[0.1em] uppercase">
              {country.subregion}
            </span>
          )}
        </div>
        <span className="font-mono text-gold3 mt-auto text-[10px] tracking-[0.15em] uppercase">
          Открыть досье <ArrowNext />
        </span>
      </Link>
    </Card>
  );
}
