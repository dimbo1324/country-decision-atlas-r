import Link from "next/link";

import { routesApi } from "../../../shared/api/routes";
import { normalizeLocale } from "../../../shared/lib/locale";
import { routes } from "../../../shared/lib/routes";
import { ErrorState } from "../../../shared/ui/ErrorState";
import { RouteDetailView } from "../../../features/routes";

export const dynamic = "force-dynamic";

type PageProps = {
  params: Promise<{ id: string }>;
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

export default async function RoutePage({ params, searchParams }: PageProps) {
  const { id } = await params;
  const resolvedSearchParams = await searchParams;
  const rawLocale = resolvedSearchParams["locale"];
  const locale = normalizeLocale(typeof rawLocale === "string" ? rawLocale : undefined);

  try {
    const route = await routesApi.getRoute(id, { locale });
    return (
      <div className="pageShell">
        <nav className="breadcrumbs" aria-label="Навигация">
          <Link
            href={`${routes.countries}?locale=${locale}`}
            className="breadcrumbLink"
          >
            Страны
          </Link>
          <span className="breadcrumbSep" aria-hidden="true">
            /
          </span>
          <Link
            href={routes.countryWithLocale(route.country_slug, locale)}
            className="breadcrumbLink"
          >
            {route.country_slug}
          </Link>
          <span className="breadcrumbSep" aria-hidden="true">
            /
          </span>
          <span className="breadcrumbCurrent">{route.title}</span>
        </nav>
        <RouteDetailView route={route} locale={locale} />
      </div>
    );
  } catch (err: unknown) {
    const errProp =
      err instanceof Error
        ? err.message
        : (err as { error?: { code?: string; message?: string } });
    return (
      <div className="pageShell">
        <nav className="breadcrumbs" aria-label="Навигация">
          <Link
            href={`${routes.countries}?locale=${locale}`}
            className="breadcrumbLink"
          >
            Страны
          </Link>
          <span className="breadcrumbSep" aria-hidden="true">
            /
          </span>
          <span className="breadcrumbCurrent">{id}</span>
        </nav>
        <header className="pageHeader">
          <p className="eyebrow">Маршрут</p>
          <h1>{id}</h1>
        </header>
        <ErrorState
          error={errProp}
          backHref={`${routes.countries}?locale=${locale}`}
          backLabel="Назад к странам"
        />
      </div>
    );
  }
}
