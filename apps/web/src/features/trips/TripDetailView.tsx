"use client";

import { useQuery } from "@tanstack/react-query";
import { Badge, Button, Card, Kicker } from "@country-decision-atlas/ui";
import { Link, useRouter } from "../../i18n/navigation";
import { tripQuery, useDeleteTripMutation } from "../../entities/trips/api";
import { isApiError } from "../../shared/api/http";
import { useAuth } from "../../shared/auth/AuthProvider";
import { routes } from "../../shared/lib/routes";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";
import { TripChecklist } from "./TripChecklist";
import { TripReminders } from "./TripReminders";
import { TripShareExport } from "./TripShareExport";
import { TripWarnings } from "./TripWarnings";
import { TripWaypoints } from "./TripWaypoints";

const TRIP_STATUS_LABELS: Record<string, string> = {
  draft: "Черновик",
  active: "Активна",
  completed: "Завершена",
  abandoned: "Отменена",
};

export function TripDetailView({ tripId }: { tripId: string }) {
  const { user, isLoading: isAuthLoading } = useAuth();
  const router = useRouter();
  const trip = useQuery({ ...tripQuery(tripId), enabled: Boolean(user) });
  const deleteTrip = useDeleteTripMutation();

  if (isAuthLoading) {
    return <LoadingState message="Загрузка…" />;
  }

  if (!user) {
    return (
      <div
        className="notice"
        data-testid="trip-detail-unauthenticated"
      >
        Войдите, чтобы просмотреть поездку.{" "}
        <Link href={routes.login}>Войти</Link>
      </div>
    );
  }

  if (trip.isPending) {
    return <LoadingState message="Загрузка поездки…" />;
  }

  if (trip.isError) {
    return (
      <div data-testid="trip-detail-error">
        <ErrorState error={isApiError(trip.error) ? trip.error : undefined} />
      </div>
    );
  }

  const item = trip.data.item;

  async function handleDelete() {
    await deleteTrip.mutateAsync(tripId);
    router.push(routes.trips);
  }

  return (
    <div
      className="flex flex-col gap-8"
      data-testid="trip-detail"
    >
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-col gap-2">
          <Kicker>Поездка</Kicker>
          <h1
            className="font-display text-3xl font-bold"
            data-testid="trip-title"
          >
            {item.title}
          </h1>
          <div className="flex flex-wrap gap-2">
            <Badge variant="default">
              {TRIP_STATUS_LABELS[item.status] ?? item.status}
            </Badge>
            {item.origin_country && (
              <Badge variant="default">Из: {item.origin_country.name}</Badge>
            )}
          </div>
        </div>
        <Button
          variant="ghost"
          onClick={handleDelete}
          disabled={deleteTrip.isPending}
          className="text-terra3 hover:text-terra2"
          data-testid="trip-delete-button"
        >
          Удалить поездку
        </Button>
      </div>

      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <Kicker>Маршрут</Kicker>
        <TripWaypoints
          tripId={tripId}
          waypoints={item.waypoints ?? []}
        />
      </Card>

      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <Kicker>Чек-лист</Kicker>
        <TripChecklist
          tripId={tripId}
          items={item.checklist_items ?? []}
        />
      </Card>

      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <Kicker>Напоминания</Kicker>
        <TripReminders
          tripId={tripId}
          reminders={item.reminders ?? []}
        />
      </Card>

      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <Kicker>Предупреждения</Kicker>
        <TripWarnings tripId={tripId} />
      </Card>

      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <Kicker>Публикация</Kicker>
        <TripShareExport trip={item} />
      </Card>
    </div>
  );
}
