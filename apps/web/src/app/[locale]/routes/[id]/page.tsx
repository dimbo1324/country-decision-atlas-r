import { getLocale } from "next-intl/server";
import { getPathname, Link } from "../../../../i18n/navigation";
import { routesApi } from "../../../../shared/api/routes";
import { asSupportedLocale } from "../../../../shared/lib/locale";
import { routes } from "../../../../shared/lib/routes";
import { DisclaimerNotice } from "../../../../shared/ui/DisclaimerNotice";
import { ErrorState } from "../../../../shared/ui/ErrorState";
import { RouteDetailView } from "../../../../features/routes";

export const dynamic = "force-dynamic";

type PageProps = {
  params: Promise<{ id: string }>;
};

export default async function RoutePage({ params }: PageProps) {
  const { id } = await params;
  const locale = asSupportedLocale(await getLocale());

  try {
    const route = await routesApi.getRoute(id, { locale });
    return (
      <div className="pageShell">
        <nav
          className="breadcrumbs"
          aria-label="Навигация"
        >
          <Link
            href={routes.countries}
            className="breadcrumbLink"
          >
            Страны
          </Link>
          <span
            className="breadcrumbSep"
            aria-hidden="true"
          >
            /
          </span>
          <Link
            href={routes.country(route.country_slug)}
            className="breadcrumbLink"
          >
            {route.country_slug}
          </Link>
          <span
            className="breadcrumbSep"
            aria-hidden="true"
          >
            /
          </span>
          <span className="breadcrumbCurrent">{route.title}</span>
        </nav>
        <RouteDetailView route={route} />
        <DisclaimerNotice />
      </div>
    );
  } catch (err: unknown) {
    const errProp =
      err instanceof Error
        ? err.message
        : (err as { error?: { code?: string; message?: string } });
    return (
      <div className="pageShell">
        <nav
          className="breadcrumbs"
          aria-label="Навигация"
        >
          <Link
            href={routes.countries}
            className="breadcrumbLink"
          >
            Страны
          </Link>
          <span
            className="breadcrumbSep"
            aria-hidden="true"
          >
            /
          </span>
          <span className="breadcrumbCurrent">{id}</span>
        </nav>
        <header className="pageHeader">
          <p className="eyebrow">Маршрут</p>
          <h1>Маршрут не найден</h1>
        </header>
        <ErrorState
          error={errProp}
          backHref={getPathname({ href: routes.countries, locale })}
          backLabel="Назад к странам"
        />
      </div>
    );
  }
}
