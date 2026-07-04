"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { isApiError } from "../../shared/api/http";
import { watchlistsApi } from "../../shared/api/watchlists";
import { useAuth } from "../../shared/auth/AuthProvider";
import { routes } from "../../shared/lib/routes";

type WatchlistButtonState =
  | "loading"
  | "saved"
  | "unsaved"
  | "error"
  | "disabled"
  | "login-required";

export function WatchlistButton({ countrySlug }: { countrySlug: string }) {
  const { user, isLoading: isAuthLoading } = useAuth();
  const [state, setState] = useState<WatchlistButtonState>("loading");

  useEffect(() => {
    if (isAuthLoading) return;
    if (!user) {
      setState("login-required");
      return;
    }
    let active = true;
    setState("loading");
    watchlistsApi
      .getCountryWatchlistStatus(countrySlug)
      .then((response) => {
        if (active) setState(response.saved ? "saved" : "unsaved");
      })
      .catch((err: unknown) => {
        if (!active) return;
        if (isApiError(err) && err.error?.code === "feature_disabled") {
          setState("disabled");
        } else {
          setState("error");
        }
      });
    return () => {
      active = false;
    };
  }, [user, isAuthLoading, countrySlug]);

  async function handleToggle() {
    if (state === "saved") {
      setState("loading");
      try {
        await watchlistsApi.removeCountryFromWatchlist(countrySlug);
        setState("unsaved");
      } catch {
        setState("error");
      }
    } else if (state === "unsaved") {
      setState("loading");
      try {
        await watchlistsApi.addCountryToWatchlist(countrySlug);
        setState("saved");
      } catch {
        setState("error");
      }
    }
  }

  if (isAuthLoading || state === "loading") {
    return (
      <span
        className="notice"
        data-testid="watchlist-button-loading"
      >
        Загрузка…
      </span>
    );
  }

  if (state === "login-required") {
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

  if (state === "disabled") {
    return null;
  }

  if (state === "error") {
    return (
      <span
        className="notice"
        data-testid="watchlist-button-error"
      >
        Не удалось загрузить статус watchlist.
      </span>
    );
  }

  return (
    <button
      type="button"
      className="runButton"
      onClick={handleToggle}
      data-testid="watchlist-toggle-button"
    >
      {state === "saved" ? "В watchlist ✓" : "Сохранить в watchlist"}
    </button>
  );
}
