import { getLocale } from "next-intl/server";
import { Kicker } from "@country-decision-atlas/ui";
import { getPathname, Link } from "../../../../i18n/navigation";
import { countriesApi } from "../../../../shared/api";
import { asSupportedLocale, toApiLocale } from "../../../../shared/lib/locale";
import { routes } from "../../../../shared/lib/routes";
import { ErrorState } from "../../../../shared/ui/ErrorState";
import {
  CountryHeader,
  CountryDossier,
} from "../../../../features/country-card";
import { WatchlistButton } from "../../../../features/watchlist";

type PageProps = {
  params: Promise<{ slug: string }>;
};

export default async function CountryPage({ params }: PageProps) {
  const { slug } = await params;
  const locale = asSupportedLocale(await getLocale());

  let card;
  try {
    card = await countriesApi.getCountryCard(slug, toApiLocale(locale));
  } catch (err: unknown) {
    const errProp =
      err instanceof Error
        ? err.message
        : (err as { error?: { code?: string; message?: string } });
    return (
      <div className="flex flex-col gap-6">
        <nav
          aria-label="Навигация"
          className="text-c4 flex items-center gap-2 text-xs"
        >
          <Link
            href={routes.countries}
            className="hover:text-gold transition-colors duration-300"
          >
            Страны
          </Link>
          <span aria-hidden="true">/</span>
          <span>{slug}</span>
        </nav>
        <header className="flex flex-col gap-3">
          <Kicker>Страна</Kicker>
          <h1 className="font-display text-3xl font-bold">{slug}</h1>
        </header>
        <ErrorState
          error={errProp}
          backHref={getPathname({ href: routes.countries, locale })}
          backLabel="Назад к странам"
        />
      </div>
    );
  }

  const isFallback = card.locale.translation_status === "fallback";

  return (
    <div className="flex flex-col gap-6">
      <nav
        aria-label="Навигация"
        className="text-c4 flex items-center gap-2 text-xs"
      >
        <Link
          href={routes.countries}
          className="hover:text-gold transition-colors duration-300"
        >
          Страны
        </Link>
        <span aria-hidden="true">/</span>
        <span>{card.country.name}</span>
      </nav>

      {isFallback && (
        <p className="border-terra2/60 text-terra3 border px-4 py-3 text-sm">
          Русский перевод частично отсутствует. Показана английская
          fallback-версия.
        </p>
      )}

      <CountryHeader country={card.country} />

      <div data-testid="watchlist-button-container">
        <WatchlistButton
          countrySlug={card.country.slug}
          countryName={card.country.name}
        />
      </div>

      <CountryDossier
        card={card}
        locale={locale}
      />
    </div>
  );
}
