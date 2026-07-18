"use client";

import { useQuery } from "@tanstack/react-query";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import {
  Badge,
  BoardGrid,
  Button,
  Card,
  Field,
  FieldError,
  FieldLabel,
  Kicker,
  toast,
} from "@country-decision-atlas/ui";
import { Link } from "../../i18n/navigation";
import { allCountriesQuery, scenariosQuery } from "../../entities/decision/api";
import { tripsQuery, useCreateTripMutation } from "../../entities/trips/api";
import { isApiError } from "../../shared/api/http";
import { useAuth } from "../../shared/auth/AuthProvider";
import { useAppLocale } from "../../shared/lib/useAppLocale";
import { routes } from "../../shared/lib/routes";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";

const TRIP_STATUS_LABELS: Record<string, string> = {
  draft: "Черновик",
  active: "Активна",
  completed: "Завершена",
  abandoned: "Отменена",
};

const inputClass =
  "border-warm bg-bg2 text-c1 font-body border px-4 py-2.5 text-sm outline-none focus-visible:border-gold transition-colors duration-200";
const selectClass =
  "border-warm bg-bg2 text-c2 focus-visible:border-gold w-full border px-3 py-2 text-sm outline-none";

const createTripSchema = z.object({
  title: z.string().min(1, "Введите название поездки"),
  originCountrySlug: z.string().optional(),
  scenarioSlug: z.string().optional(),
});
type CreateTripValues = z.infer<typeof createTripSchema>;

function CreateTripForm() {
  const locale = useAppLocale();
  const countries = useQuery(allCountriesQuery(locale));
  const scenarios = useQuery(scenariosQuery(locale));
  const createTrip = useCreateTripMutation();
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<CreateTripValues>({ resolver: zodResolver(createTripSchema) });

  async function onSubmit(values: CreateTripValues) {
    try {
      await createTrip.mutateAsync({
        title: values.title,
        origin_country_slug: values.originCountrySlug || null,
        scenario_slug: values.scenarioSlug || null,
        status: "draft",
      });
      reset();
      toast.success("Поездка создана.");
    } catch (err: unknown) {
      toast.error(
        isApiError(err)
          ? (err.error?.message ?? "Не удалось создать поездку.")
          : "Не удалось создать поездку.",
      );
    }
  }

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="flex flex-col gap-4"
      noValidate
    >
      <Field>
        <FieldLabel htmlFor="trip-title">Название поездки</FieldLabel>
        <input
          id="trip-title"
          type="text"
          className={inputClass}
          data-testid="trip-title-input"
          {...register("title")}
        />
        <FieldError>{errors.title?.message}</FieldError>
      </Field>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Field>
          <FieldLabel htmlFor="trip-origin">Страна отправления</FieldLabel>
          <select
            id="trip-origin"
            className={selectClass}
            data-testid="trip-origin-select"
            {...register("originCountrySlug")}
          >
            <option value="">Не указано</option>
            {countries.data?.items.map((c) => (
              <option
                key={c.slug}
                value={c.slug}
              >
                {c.name}
              </option>
            ))}
          </select>
        </Field>
        <Field>
          <FieldLabel htmlFor="trip-scenario">Сценарий</FieldLabel>
          <select
            id="trip-scenario"
            className={selectClass}
            data-testid="trip-scenario-select"
            {...register("scenarioSlug")}
          >
            <option value="">Не указано</option>
            {scenarios.data?.items.map((s) => (
              <option
                key={s.slug}
                value={s.slug}
              >
                {s.name}
              </option>
            ))}
          </select>
        </Field>
      </div>
      <Button
        type="submit"
        disabled={createTrip.isPending}
        data-testid="trip-create-submit"
      >
        {createTrip.isPending ? "Создаём…" : "Создать поездку"}
      </Button>
    </form>
  );
}

export function TripListView() {
  const { user, isLoading: isAuthLoading } = useAuth();
  const trips = useQuery({ ...tripsQuery(), enabled: Boolean(user) });

  if (isAuthLoading) {
    return <LoadingState message="Загрузка…" />;
  }

  if (!user) {
    return (
      <div
        className="border-warm flex flex-col gap-2 border px-4 py-4"
        data-testid="trips-unauthenticated"
      >
        <p className="text-c3 text-sm">
          Войдите, чтобы планировать поездки.{" "}
          <Link
            href={routes.login}
            className="text-c1 hover:text-gold3 underline decoration-dotted underline-offset-2 transition-colors duration-200"
          >
            Войти
          </Link>
        </p>
      </div>
    );
  }

  if (trips.isPending) {
    return <LoadingState message="Загрузка поездок…" />;
  }

  if (trips.isError) {
    return (
      <div data-testid="trips-error">
        <ErrorState error={isApiError(trips.error) ? trips.error : undefined} />
      </div>
    );
  }

  const items = trips.data.items ?? [];

  return (
    <div
      className="flex flex-col gap-8"
      data-testid="trips-view"
    >
      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <Kicker>Новая поездка</Kicker>
        <CreateTripForm />
      </Card>

      <div className="flex flex-col gap-4">
        <Kicker>Мои поездки</Kicker>
        {items.length === 0 ? (
          <div data-testid="trips-empty-state">
            <EmptyState message="Поездок пока нет. Создайте первую выше." />
          </div>
        ) : (
          <BoardGrid data-testid="trips-list">
            {items.map((trip) => (
              <Link
                key={trip.id}
                href={routes.tripDetail(trip.id)}
                data-testid="trip-item"
              >
                <Card className="flex h-full flex-col gap-3">
                  <span className="font-display text-lg font-semibold">
                    {trip.title}
                  </span>
                  <div className="flex flex-wrap gap-2">
                    <Badge variant="default">
                      {TRIP_STATUS_LABELS[trip.status] ?? trip.status}
                    </Badge>
                    {trip.origin_country && (
                      <Badge variant="default">
                        Из: {trip.origin_country.name}
                      </Badge>
                    )}
                  </div>
                </Card>
              </Link>
            ))}
          </BoardGrid>
        )}
      </div>
    </div>
  );
}
