import Link from "next/link";

import { countriesApi } from "../../shared/api";
import { getLocaleFromSearchParams } from "../../shared/lib/locale";
import { routes } from "../../shared/lib/routes";
import { EmptyState } from "../../shared/ui/EmptyState";
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
  } catch (err: unknown) {
    const errProp =
      err instanceof Error
        ? err.message
        : (err as { error?: { code?: string; message?: string } });
    return (
      <div className="pageShell">
        <header className="pageHeader">
          <p className="eyebrow">Страны</p>
          <h1>Карточки стран для подбора</h1>
        </header>
        <ErrorState error={errProp} backHref={routes.home} backLabel="На главную" />
      </div>
    );
  }

  return (
    <div className="pageShell">
      <header className="pageHeader">
        <p className="eyebrow">Страны</p>
        <h1>Карточки стран для подбора</h1>
        <p className="pageSubtitle">
          Каждая карточка страны содержит сценарные оценки, правовые сигналы,
          доказательства с источниками и профильные разделы для принятия решений.
        </p>
      </header>

      {countries.items.length === 0 ? (
        <EmptyState message="Страны пока отсутствуют." />
      ) : (
        <div className="countryCardGrid">
          {countries.items.map((country) => (
            <div key={country.slug} className="countryPreviewCard">
              <div className="countryPreviewTop">
                <span className="countryPreviewName">{country.name}</span>
                <div className="countryPreviewMeta">
                  {country.iso2 && <span className="metaChip">{country.iso2}</span>}
                  {country.region && <span className="metaChip">{country.region}</span>}
                </div>
              </div>
              <div className="countryPreviewActions">
                <Link
                  href={`${routes.country(country.slug)}?locale=${locale}`}
                  className="countryPreviewLink countryPreviewLinkPrimary"
                >
                  Карточка страны
                </Link>
                <Link
                  href={`${routes.decision}?locale=${locale}`}
                  className="countryPreviewLink"
                >
                  Запустить подбор
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="countryPageFooter">
        <Link href={`${routes.decision}?locale=${locale}`} className="footerAction">
          Сравнение Россия vs Уругвай →
        </Link>
      </div>
    </div>
  );
}
