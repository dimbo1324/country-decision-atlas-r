import { getLocale } from "next-intl/server";
import { Badge, Card, Kicker } from "@country-decision-atlas/ui";
import { getPathname, Link } from "../../../../../i18n/navigation";
import { getSharedTrip } from "../../../../../entities/trips/api";
import { ErrorState } from "../../../../../shared/ui/ErrorState";

export const dynamic = "force-dynamic";

const TRIP_STATUS_LABELS: Record<string, string> = {
  draft: "Черновик",
  active: "Активна",
  completed: "Завершена",
  abandoned: "Отменена",
};

const WAYPOINT_KIND_LABELS: Record<string, string> = {
  transit: "Транзит",
  destination: "Назначение",
  stopover: "Остановка",
};

const CHECKLIST_STATUS_LABELS: Record<string, string> = {
  todo: "Не начато",
  in_progress: "В процессе",
  done: "Готово",
  skipped: "Пропущено",
};

type PageProps = {
  params: Promise<{ token: string }>;
};

export default async function SharedTripPage({ params }: PageProps) {
  const { token } = await params;
  const locale = await getLocale();

  try {
    const trip = await getSharedTrip(token);
    return (
      <div
        className="flex flex-col gap-6"
        data-testid="shared-trip-page"
      >
        <header className="flex flex-col gap-3">
          <Kicker>Публичная поездка</Kicker>
          <h1
            className="font-display text-3xl font-bold"
            data-testid="shared-trip-title"
          >
            {trip.title}
          </h1>
          <div className="flex flex-wrap gap-2">
            <Badge variant="default">
              {TRIP_STATUS_LABELS[trip.status] ?? trip.status}
            </Badge>
            {trip.origin_country && (
              <Badge variant="default">Из: {trip.origin_country.name}</Badge>
            )}
          </div>
        </header>

        <Card
          interactive={false}
          className="flex flex-col gap-3"
        >
          <h2 className="font-display text-lg font-semibold">Маршрут</h2>
          {trip.waypoints.length === 0 ? (
            <p className="text-c3 text-sm">Маршрут пуст.</p>
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
                      {WAYPOINT_KIND_LABELS[waypoint.kind] ?? waypoint.kind}
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
          <h2 className="font-display text-lg font-semibold">Чек-лист</h2>
          {trip.checklist_items.length === 0 ? (
            <p className="text-c3 text-sm">Чек-лист пуст.</p>
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
                      {CHECKLIST_STATUS_LABELS[item.status] ?? item.status}
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
          <Kicker>Публичная поездка</Kicker>
          <h1 className="font-display text-3xl font-bold">
            Поездка недоступна
          </h1>
        </header>
        <ErrorState
          error={errProp}
          backHref={getPathname({ href: "/", locale })}
          backLabel="На главную"
        />
        <Link
          href="/"
          className="text-gold3 hover:text-gold text-sm transition-colors duration-300"
        >
          На главную
        </Link>
      </div>
    );
  }
}
