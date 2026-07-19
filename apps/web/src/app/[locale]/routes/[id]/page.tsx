import { getLocale, getTranslations } from "next-intl/server";
import { Kicker } from "@country-decision-atlas/ui";
import { getPathname } from "../../../../i18n/navigation";
import { routesApi } from "../../../../shared/api/routes";
import { asSupportedLocale, toApiLocale } from "../../../../shared/lib/locale";
import { routes } from "../../../../shared/lib/routes";
import { AppBreadcrumbs } from "../../../../shared/ui/AppBreadcrumbs";
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
  const t = await getTranslations("routePage");

  try {
    const route = await routesApi.getRoute(id, { locale: toApiLocale(locale) });
    return (
      <div className="flex flex-col gap-6">
        <AppBreadcrumbs
          items={[
            { label: t("countries"), href: routes.countries },
            {
              label: route.country_slug,
              href: routes.country(route.country_slug),
            },
            { label: route.title },
          ]}
        />
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
      <div className="flex flex-col gap-6">
        <AppBreadcrumbs
          items={[
            { label: t("countries"), href: routes.countries },
            { label: id },
          ]}
        />
        <header className="flex flex-col gap-3">
          <Kicker>{t("kicker")}</Kicker>
          <h1 className="font-display text-4xl font-bold">{t("notFound")}</h1>
        </header>
        <ErrorState
          error={errProp}
          backHref={getPathname({ href: routes.countries, locale })}
          backLabel={t("backToCountries")}
        />
      </div>
    );
  }
}
