import { getLocale, getTranslations } from "next-intl/server";
import { Badge, Card, Kicker } from "@country-decision-atlas/ui";
import { getPathname, Link } from "../../../../../i18n/navigation";
import { getSharedTrip } from "../../../../../entities/trips/api";
import { asSupportedLocale } from "../../../../../shared/lib/locale";
import { ErrorState } from "../../../../../shared/ui/ErrorState";
import {
  TRIP_STATUS_LABELS,
  WAYPOINT_KIND_LABELS,
} from "../../../../../features/trips/trip-labels";

export const dynamic = "force-dynamic";

const CHECKLIST_STATUS_LABELS: Record<string, Record<string, string>> = {
  en: {
    todo: "Not started",
    in_progress: "In progress",
    done: "Done",
    skipped: "Skipped",
  },
  ru: {
    todo: "Не начато",
    in_progress: "В процессе",
    done: "Готово",
    skipped: "Пропущено",
  },
  es: {
    todo: "No iniciado",
    in_progress: "En curso",
    done: "Hecho",
    skipped: "Omitido",
  },
};

type PageProps = {
  params: Promise<{ token: string }>;
};

export default async function SharedTripPage({ params }: PageProps) {
  const { token } = await params;
  const localeParam = await getLocale();
  const locale = asSupportedLocale(localeParam);
  const t = await getTranslations("sharedTripPage");

  try {
    const trip = await getSharedTrip(token);
    return (
      <div
        className="flex flex-col gap-6"
        data-testid="shared-trip-page"
      >
        <header className="flex flex-col gap-3">
          <Kicker>{t("kicker")}</Kicker>
          <h1
            className="font-display text-3xl font-bold"
            data-testid="shared-trip-title"
          >
            {trip.title}
          </h1>
          <div className="flex flex-wrap gap-2">
            <Badge variant="default">
              {TRIP_STATUS_LABELS[locale][trip.status] ?? trip.status}
            </Badge>
            {trip.origin_country && (
              <Badge variant="default">
                {t("from", { name: trip.origin_country.name })}
              </Badge>
            )}
          </div>
        </header>

        <Card
          interactive={false}
          className="flex flex-col gap-3"
        >
          <h2 className="font-display text-lg font-semibold">{t("route")}</h2>
          {trip.waypoints.length === 0 ? (
            <p className="text-c3 text-sm">{t("routeEmpty")}</p>
          ) : (
            <div className="flex flex-col gap-2">
              {trip.waypoints
                .slice()
                .sort((a, b) => a.position - b.position)
                .map((waypoint, index) => (
                  <div
                    key={`${waypoint.country.slug}-${index}`}
                    className="border-warm flex items-center gap-3 border-b py-2 last:border-b-0"
                  >
                    <span className="text-c2 flex-1 text-sm">
                      {waypoint.country.name}
                      {waypoint.city ? ` · ${waypoint.city}` : ""}
                    </span>
                    <Badge variant="default">
                      {WAYPOINT_KIND_LABELS[locale][waypoint.kind] ??
                        waypoint.kind}
                    </Badge>
                  </div>
                ))}
            </div>
          )}
        </Card>

        <Card
          interactive={false}
          className="flex flex-col gap-3"
        >
          <h2 className="font-display text-lg font-semibold">
            {t("checklist")}
          </h2>
          {trip.checklist_items.length === 0 ? (
            <p className="text-c3 text-sm">{t("checklistEmpty")}</p>
          ) : (
            <div className="flex flex-col gap-2">
              {trip.checklist_items
                .slice()
                .sort((a, b) => a.position - b.position)
                .map((item, index) => (
                  <div
                    key={`${item.title}-${index}`}
                    className="border-warm flex items-center gap-3 border-b py-2 last:border-b-0"
                  >
                    <span className="text-c2 flex-1 text-sm">{item.title}</span>
                    <Badge variant="default">
                      {CHECKLIST_STATUS_LABELS[locale][item.status] ??
                        item.status}
                    </Badge>
                  </div>
                ))}
            </div>
          )}
        </Card>
      </div>
    );
  } catch (err: unknown) {
    const errProp =
      err instanceof Error
        ? err.message
        : (err as { error?: { code?: string; message?: string } });
    return (
      <div className="flex flex-col gap-6">
        <header className="flex flex-col gap-3">
          <Kicker>{t("kicker")}</Kicker>
          <h1 className="font-display text-3xl font-bold">
            {t("unavailable")}
          </h1>
        </header>
        <ErrorState
          error={errProp}
          backHref={getPathname({ href: "/", locale })}
          backLabel={t("home")}
        />
        <Link
          href="/"
          className="text-gold3 hover:text-gold text-sm transition-colors duration-300"
        >
          {t("home")}
        </Link>
      </div>
    );
  }
}
