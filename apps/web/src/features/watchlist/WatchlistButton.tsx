"use client";

import { useQuery } from "@tanstack/react-query";
import { Link } from "../../i18n/navigation";
import {
  myWatchlistQuery,
  useToggleWatchlistMutation,
} from "../../entities/watchlist/api";
import { isApiError } from "../../shared/api/http";
import { useAuth } from "../../shared/auth/AuthProvider";
import { hasSessionHint } from "../../shared/auth/session";
import { routes } from "../../shared/lib/routes";

export function WatchlistButton({
  countrySlug,
  countryName,
}: {
  countrySlug: string;
  countryName: string;
}) {
  const { user, isLoading: isAuthLoading } = useAuth();
  // Visitors with no session hint can't possibly have a saved watchlist, so
  // the query must stay disabled until we know a session might exist: any
  // client-side setState-equivalent state flip here — however brief —
  // duplicates SSR content on force-dynamic pages (see memory
  // episode_gotchas_backend_tooling.md).
  const watchlist = useQuery({
    ...myWatchlistQuery(),
    enabled: hasSessionHint() && Boolean(user) && !isAuthLoading,
  });
  const toggle = useToggleWatchlistMutation();

  if (!hasSessionHint() || (!isAuthLoading && !user)) {
    return (
      <Link
        href={routes.login}
        className="internalLink"
        data-testid="watchlist-button-login-required"
      >
        Войдите, чтобы сохранить страну
      </Link>
    );
  }

  if (isAuthLoading || watchlist.isPending) {
    return (
      <span
        className="notice"
        data-testid="watchlist-button-loading"
      >
        Загрузка…
      </span>
    );
  }

  if (watchlist.isError) {
    if (
      isApiError(watchlist.error) &&
      watchlist.error.error?.code === "feature_disabled"
    ) {
      return null;
    }
    return (
      <span
        className="notice"
        data-testid="watchlist-button-error"
      >
        Не удалось загрузить статус watchlist.
      </span>
    );
  }

  const saved = (watchlist.data.items ?? []).some(
    (item) => item.country_slug === countrySlug,
  );

  return (
    <button
      type="button"
      className="runButton"
      onClick={() =>
        toggle.mutate({ countrySlug, countryName, nextSaved: !saved })
      }
      disabled={toggle.isPending}
      data-testid="watchlist-toggle-button"
    >
      {saved ? "В watchlist ✓" : "Сохранить в watchlist"}
    </button>
  );
}
