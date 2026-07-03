"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "../auth/AuthProvider";
import { normalizeLocale } from "../lib/locale";
import { routes, withLocale } from "../lib/routes";

export function AuthNav() {
  const { user, isLoading, logout } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const locale = normalizeLocale(searchParams.get("locale"));

  if (isLoading) {
    return null;
  }

  if (!user) {
    return (
      <Link
        href={withLocale(routes.login, locale)}
        className="navLink"
        data-testid="nav-sign-in-link"
      >
        Войти
      </Link>
    );
  }

  async function handleLogout() {
    await logout();
    router.push(routes.home);
  }

  return (
    <div className="authNav">
      <Link
        href={withLocale(routes.account, locale)}
        className="navLink"
        data-testid="nav-account-link"
      >
        Кабинет
      </Link>
      <Link
        href={withLocale(routes.watchlist, locale)}
        className="navLink"
        data-testid="nav-watchlist-link"
      >
        Watchlist
      </Link>
      <button
        type="button"
        className="navLink"
        onClick={handleLogout}
        data-testid="nav-logout-button"
      >
        Выйти
      </button>
    </div>
  );
}
