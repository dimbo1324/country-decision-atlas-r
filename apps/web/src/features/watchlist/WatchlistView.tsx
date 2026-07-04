"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { isApiError } from "../../shared/api/http";
import { watchlistsApi, type WatchlistItem } from "../../shared/api/watchlists";
import { useAuth } from "../../shared/auth/AuthProvider";
import { routes } from "../../shared/lib/routes";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";

export function WatchlistView() {
  const { user, isLoading: isAuthLoading } = useAuth();
  const [items, setItems] = useState<WatchlistItem[] | null>(null);
  const [error, setError] = useState<unknown | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!user) {
      setIsLoading(false);
      return;
    }
    let active = true;
    setIsLoading(true);
    watchlistsApi
      .listWatchlist()
      .then((response) => {
        if (active) setItems(response.items ?? []);
      })
      .catch((err: unknown) => {
        if (active) setError(err);
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });
    return () => {
      active = false;
    };
  }, [user]);

  async function handleRemove(countrySlug: string) {
    await watchlistsApi.removeCountryFromWatchlist(countrySlug);
    setItems(
      (prev) =>
        prev?.filter((item) => item.country_slug !== countrySlug) ?? null,
    );
  }

  async function handleToggle(
    countrySlug: string,
    field:
      | "notify_legal_signals"
      | "notify_drift_changes"
      | "notify_route_updates",
    value: boolean,
  ) {
    const updated = await watchlistsApi.updateWatchlistPreferences(
      countrySlug,
      {
        [field]: value,
      },
    );
    setItems(
      (prev) =>
        prev?.map((item) =>
          item.country_slug === countrySlug ? updated : item,
        ) ?? null,
    );
  }

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

  if (isLoading) {
    return <LoadingState message="Загрузка watchlist…" />;
  }

  if (error) {
    return (
      <div data-testid="watchlist-error">
        <ErrorState error={isApiError(error) ? error : undefined} />
      </div>
    );
  }

  if (!items || items.length === 0) {
    return (
      <div
        className="emptyNotice"
        data-testid="watchlist-empty-state"
      >
        Watchlist пуст. Сохраните страну на странице страны.
      </div>
    );
  }

  return (
    <div
      className="searchPageContainer"
      data-testid="watchlist-list"
    >
      {items.map((item) => (
        <div
          className="watchlistCard"
          key={item.id}
          data-testid="watchlist-item"
        >
          <div className="watchlistCardHeader">
            <Link href={routes.country(item.country_slug)}>
              {item.country_name}
            </Link>
            <button
              type="button"
              className="runButton"
              onClick={() => handleRemove(item.country_slug)}
              data-testid="watchlist-remove-button"
            >
              Удалить
            </button>
          </div>
          <div className="watchlistToggleRow">
            <label className="checkboxLabel">
              <input
                type="checkbox"
                checked={item.notify_legal_signals}
                onChange={(event) =>
                  handleToggle(
                    item.country_slug,
                    "notify_legal_signals",
                    event.target.checked,
                  )
                }
              />
              Правовые сигналы
            </label>
            <label className="checkboxLabel">
              <input
                type="checkbox"
                checked={item.notify_drift_changes}
                onChange={(event) =>
                  handleToggle(
                    item.country_slug,
                    "notify_drift_changes",
                    event.target.checked,
                  )
                }
              />
              Изменение направления
            </label>
            <label className="checkboxLabel">
              <input
                type="checkbox"
                checked={item.notify_route_updates}
                onChange={(event) =>
                  handleToggle(
                    item.country_slug,
                    "notify_route_updates",
                    event.target.checked,
                  )
                }
              />
              Обновления маршрутов
            </label>
          </div>
        </div>
      ))}
    </div>
  );
}
