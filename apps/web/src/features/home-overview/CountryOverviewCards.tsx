import {
  Badge,
  Card,
  ProgressRing,
  type BadgeVariant,
} from "@country-decision-atlas/ui";
import { Link } from "../../i18n/navigation";
import type { CountryOverviewCard } from "../../shared/api/home";
import { capitalize } from "../../shared/lib/format";
import { useAppLocale } from "../../shared/lib/useAppLocale";
import { confidenceLabel } from "../../shared/ui/ConfidenceBadge";
import { ArrowNext } from "../../shared/ui/LinkArrow";

const CONFIDENCE_VARIANT: Record<string, BadgeVariant> = {
  high: "positive",
  medium: "warning",
  low: "negative",
};

export function CountryOverviewCards({
  countries,
}: {
  countries: CountryOverviewCard[];
}) {
  const locale = useAppLocale();
  return (
    <section aria-labelledby="home-countries-title">
      <div className="mb-5 flex items-end justify-between gap-4">
        <h2
          id="home-countries-title"
          className="font-display text-2xl font-semibold"
        >
          Обзор стран
        </h2>
        <Link
          href="/countries"
          className="font-mono text-c3 hover:text-gold3 text-[10px] tracking-[0.2em] uppercase transition-colors duration-300"
        >
          Перейти к странам <ArrowNext />
        </Link>
      </div>
      <div
        className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3"
        data-testid="home-country-cards"
      >
        {countries.map((country) => (
          <Link
            key={country.slug}
            href={`/countries/${country.slug}`}
          >
            <Card className="flex h-full flex-col gap-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h3 className="font-display text-lg leading-snug font-semibold">
                    {country.name}
                  </h3>
                  {country.iso2 && (
                    <span className="font-mono text-c4 text-[9px] tracking-[0.2em] uppercase">
                      {country.iso2}
                    </span>
                  )}
                </div>
                {country.confidence && (
                  <Badge
                    variant={
                      CONFIDENCE_VARIANT[country.confidence] ?? "default"
                    }
                  >
                    {capitalize(confidenceLabel(country.confidence, locale))}
                  </Badge>
                )}
              </div>

              <div className="flex items-center justify-center py-1">
                <ProgressRing
                  value={country.average_score ?? 0}
                  label="Средний скор"
                  size={104}
                  accent="gold"
                  active
                  mode="static"
                />
              </div>

              <dl className="text-c3 flex flex-col gap-1.5 text-xs">
                <div className="flex items-center justify-between gap-2">
                  <dt className="text-c4">Сильнейший сценарий</dt>
                  <dd className="text-right">
                    {country.best_scenario_name ?? "Нет данных"}
                    {country.best_score != null &&
                      ` · ${country.best_score.toFixed(1)}`}
                  </dd>
                </div>
                <div className="flex items-center justify-between gap-2">
                  <dt className="text-c4">Слабейший сценарий</dt>
                  <dd className="text-right">
                    {country.weakest_scenario_name ?? "Нет данных"}
                    {country.weakest_score != null &&
                      ` · ${country.weakest_score.toFixed(1)}`}
                  </dd>
                </div>
              </dl>
            </Card>
          </Link>
        ))}
      </div>
    </section>
  );
}
