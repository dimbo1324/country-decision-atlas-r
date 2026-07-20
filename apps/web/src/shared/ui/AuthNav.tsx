"use client";

import {
  cn,
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@country-decision-atlas/ui";
import { ChevronDown } from "lucide-react";
import { useTranslations } from "next-intl";
import NextLink from "next/link";
import { Link, useRouter } from "../../i18n/navigation";
import { useAuth } from "../auth/AuthProvider";
import { ADMIN_ROLES, MODERATION_ROLES, hasRole } from "../auth/roles";
import { routes } from "../lib/routes";

interface AuthNavProps {
  className?: string;
  onNavigate?: () => void;
  /**
   * "flat" renders every link as a plain list (mobile drawer);
   * "menu" collapses the signed-in links into a compact dropdown so the
   * top bar keeps a bounded width for every role and locale.
   */
  variant?: "flat" | "menu";
}

const linkClass =
  "font-mono text-c3 hover:text-c1 text-[11px] tracking-[0.14em] uppercase transition-colors duration-300";

interface AuthLink {
  label: string;
  href: string;
  testId: string;
  /** /internal/** lives outside the [locale] tree and must never be
   * locale-prefixed, so it navigates through plain next/link. */
  internal?: boolean;
}

function useAuthLinks(): AuthLink[] {
  const t = useTranslations("auth");
  const tNav = useTranslations("nav");
  const { user } = useAuth();

  if (!user) return [];

  const links: AuthLink[] = [
    { label: t("account"), href: routes.account, testId: "nav-account-link" },
    {
      label: t("watchlist"),
      href: routes.watchlist,
      testId: "nav-watchlist-link",
    },
    {
      label: t("subscriptions"),
      href: routes.subscriptions,
      testId: "nav-subscriptions-link",
    },
    { label: t("trips"), href: routes.trips, testId: "nav-trips-link" },
  ];

  if (hasRole(user, ADMIN_ROLES)) {
    links.push({
      label: tNav("dataQuality"),
      href: routes.dataQuality,
      testId: "nav-data-quality-link",
      internal: true,
    });
  }
  if (hasRole(user, MODERATION_ROLES)) {
    links.push(
      {
        label: tNav("moderation"),
        href: routes.migrationBoardModeration,
        testId: "nav-migration-board-moderation-link",
        internal: true,
      },
      {
        label: tNav("communityModeration"),
        href: routes.communityModeration,
        testId: "nav-community-moderation-link",
        internal: true,
      },
    );
  }

  return links;
}

function AuthLinkItem({
  link,
  onNavigate,
  className,
}: {
  link: AuthLink;
  onNavigate?: () => void;
  className?: string;
}) {
  const sharedProps = {
    "onClick": onNavigate,
    "data-testid": link.testId,
    className,
  };
  return link.internal ? (
    <NextLink
      href={link.href}
      {...sharedProps}
    >
      {link.label}
    </NextLink>
  ) : (
    <Link
      href={link.href}
      {...sharedProps}
    >
      {link.label}
    </Link>
  );
}

export function AuthNav({
  className,
  onNavigate,
  variant = "flat",
}: AuthNavProps) {
  const t = useTranslations("auth");
  const { user, isLoading, logout } = useAuth();
  const router = useRouter();
  const links = useAuthLinks();

  // Fixed min-width sized for the longest translation ("Iniciar sesión")
  // so this slot's own footprint -- and the gap between it and the rest
  // of the header -- doesn't shift when the interface locale changes OR
  // when the session check resolves. `invisible` (not `hidden`) keeps the
  // reserved width in the layout while a session-hint holder's refresh()
  // is still in flight, so the header doesn't collapse then re-expand a
  // beat later (see AuthProvider's isLoading/hydration notes).
  if (isLoading) {
    return (
      <span
        aria-hidden="true"
        className={cn(
          linkClass,
          "invisible inline-block min-w-[8rem]",
          className,
        )}
      >
        {t("signIn")}
      </span>
    );
  }

  if (!user) {
    return (
      // Right-aligned only from `lg` up (the desktop header copy): the
      // mobile drawer copy (below `lg`) keeps its original left-aligned
      // look, since this same component also renders there via MobileNav.
      <Link
        href={routes.login}
        onClick={onNavigate}
        className={cn(
          linkClass,
          "inline-block min-w-[8rem] lg:text-right",
          className,
        )}
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

  if (variant === "menu") {
    return (
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <button
            type="button"
            className={cn(
              linkClass,
              "flex items-center gap-1.5 outline-none",
              className,
            )}
            data-testid="nav-account-menu-trigger"
          >
            {t("account")}
            <ChevronDown
              width={12}
              height={12}
              strokeWidth={1.5}
            />
          </button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          {links.map((link) => (
            <DropdownMenuItem
              key={link.testId}
              asChild
            >
              <AuthLinkItem
                link={link}
                onNavigate={onNavigate}
                className="font-mono text-[11px] tracking-[0.14em] uppercase"
              />
            </DropdownMenuItem>
          ))}
          <DropdownMenuSeparator />
          <DropdownMenuItem
            onSelect={() => void handleLogout()}
            data-testid="nav-logout-button"
            className="font-mono text-[11px] tracking-[0.14em] uppercase"
          >
            {t("signOut")}
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    );
  }

  return (
    <div className={cn("flex items-center gap-5", className)}>
      {links.map((link) => (
        <AuthLinkItem
          key={link.testId}
          link={link}
          onNavigate={onNavigate}
          className={linkClass}
        />
      ))}
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
