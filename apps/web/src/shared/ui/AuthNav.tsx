"use client";

import { cn } from "@country-decision-atlas/ui";
import { useTranslations } from "next-intl";
import { Link, useRouter } from "../../i18n/navigation";
import { useAuth } from "../auth/AuthProvider";
import { routes } from "../lib/routes";

interface AuthNavProps {
  className?: string;
  onNavigate?: () => void;
}

const linkClass =
  "font-mono text-c3 hover:text-c1 text-[11px] tracking-[0.14em] uppercase transition-colors duration-300";

export function AuthNav({ className, onNavigate }: AuthNavProps) {
  const t = useTranslations("auth");
  const { user, isLoading, logout } = useAuth();
  const router = useRouter();

  if (isLoading) {
    return null;
  }

  if (!user) {
    return (
      <Link
        href={routes.login}
        onClick={onNavigate}
        className={cn(linkClass, className)}
        data-testid="nav-sign-in-link"
      >
        {t("signIn")}
      </Link>
    );
  }

  async function handleLogout() {
    await logout();
    onNavigate?.();
    router.push(routes.home);
  }

  return (
    <div className={cn("flex items-center gap-5", className)}>
      <Link
        href={routes.account}
        onClick={onNavigate}
        className={linkClass}
        data-testid="nav-account-link"
      >
        {t("account")}
      </Link>
      <Link
        href={routes.watchlist}
        onClick={onNavigate}
        className={linkClass}
        data-testid="nav-watchlist-link"
      >
        {t("watchlist")}
      </Link>
      <Link
        href={routes.subscriptions}
        onClick={onNavigate}
        className={linkClass}
        data-testid="nav-subscriptions-link"
      >
        {t("subscriptions")}
      </Link>
      <button
        type="button"
        className={linkClass}
        onClick={handleLogout}
        data-testid="nav-logout-button"
      >
        {t("signOut")}
      </button>
    </div>
  );
}
