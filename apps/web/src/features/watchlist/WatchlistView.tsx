"use client";

import { useQuery } from "@tanstack/react-query";
import { Badge, Card } from "@country-decision-atlas/ui";
import { Link } from "../../i18n/navigation";
import {
  myWatchlistQuery,
  useToggleWatchlistMutation,
  useUpdateWatchlistPreferencesMutation,
} from "../../entities/watchlist/api";
import { isApiError } from "../../shared/api/http";
import { useAuth } from "../../shared/auth/AuthProvider";
import { routes } from "../../shared/lib/routes";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";

const NOTIFY_TOGGLES: {
  field:
    | "notify_legal_signals"
    | "notify_drift_changes"
    | "notify_route_updates";
  label: string;
}[] = [
  { field: "notify_legal_signals", label: "Правовые сигналы" },
  { field: "notify_drift_changes", label: "Изменение направления" },
  { field: "notify_route_updates", label: "Обновления маршрутов" },
];

export function WatchlistView() {
  const { user, isLoading: isAuthLoading } = useAuth();
  const watchlist = useQuery({ ...myWatchlistQuery(), enabled: Boolean(user) });
  const toggle = useToggleWatchlistMutation();
  const updatePreferences = useUpdateWatchlistPreferencesMutation();

  if (isAuthLoading) {
    return <LoadingState message="Загрузка…" />;
  }

  if (!user) {
    return (
      <div
        className="notice"
        data-testid="watchlist-unauthenticated"
      >
        Войдите, чтобы сохранять страны в watchlist.{" "}
        <Link href={routes.login}>Войти</Link>
      </div>
    );
  }

  if (watchlist.isPending) {
    return <LoadingState message="Загрузка watchlist…" />;
  }

  if (watchlist.isError) {
    return (
      <div data-testid="watchlist-error">
        <ErrorState
          error={isApiError(watchlist.error) ? watchlist.error : undefined}
        />
      </div>
    );
  }

  const items = watchlist.data.items ?? [];

  if (items.length === 0) {
    return (
      <div data-testid="watchlist-empty-state">
        <EmptyState message="Watchlist пуст. Сохраните страну на странице страны." />
      </div>
    );
  }

  return (
    <div
      className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
      data-testid="watchlist-list"
    >
      {items.map((item) => (
        <Card
          key={item.id}
          interactive={false}
          className="flex flex-col gap-4"
          data-testid="watchlist-item"
        >
          <div className="flex items-center justify-between gap-3">
            <Link
              href={routes.country(item.country_slug)}
              className="font-display text-lg font-semibold"
            >
              {item.country_name}
            </Link>
            <button
              type="button"
              onClick={() =>
                toggle.mutate({
                  countrySlug: item.country_slug,
                  countryName: item.country_name,
                  nextSaved: false,
                })
              }
              disabled={toggle.isPending}
              data-testid="watchlist-remove-button"
              className="font-mono text-c3 hover:text-terra3 text-[10px] tracking-[0.2em] uppercase transition-colors duration-300"
            >
              Удалить
            </button>
          </div>
          <Badge variant="default">{item.status}</Badge>
          <div className="flex flex-col gap-2">
            {NOTIFY_TOGGLES.map(({ field, label }) => (
              <label
                key={field}
                className="text-c3 flex items-center gap-2 text-sm"
              >
                <input
                  type="checkbox"
                  className="accent-gold"
                  checked={item[field]}
                  onChange={(event) =>
                    updatePreferences.mutate({
                      countrySlug: item.country_slug,
                      payload: { [field]: event.target.checked },
                    })
                  }
                />
                {label}
              </label>
            ))}
          </div>
        </Card>
      ))}
    </div>
  );
}
