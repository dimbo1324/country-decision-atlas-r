"use client";

import { useTranslations } from "next-intl";
import { cn } from "@country-decision-atlas/ui";
import { Star } from "lucide-react";
import { Link } from "../../i18n/navigation";
import { useToggleWatchlistMutation } from "../../entities/watchlist/api";
import { routes } from "../../shared/lib/routes";

const STAR_BUTTON_CLASS =
  "border-warm bg-bg2/80 flex h-8 w-8 items-center justify-center border backdrop-blur-sm transition-colors duration-300";

export function WatchlistStar({
  countrySlug,
  countryName,
  saved,
  authenticated,
}: {
  countrySlug: string;
  countryName: string;
  saved: boolean;
  authenticated: boolean;
}) {
  const t = useTranslations("countryCatalog");
  const toggle = useToggleWatchlistMutation();

  if (!authenticated) {
    return (
      <Link
        href={routes.login}
        aria-label={t("loginToSave")}
        data-testid="watchlist-star-login-required"
        className={cn(STAR_BUTTON_CLASS, "text-c4 hover:text-gold3")}
      >
        <Star
          width={14}
          height={14}
          strokeWidth={1.5}
        />
      </Link>
    );
  }

  return (
    <button
      type="button"
      onClick={() =>
        toggle.mutate({ countrySlug, countryName, nextSaved: !saved })
      }
      disabled={toggle.isPending}
      aria-pressed={saved}
      aria-label={saved ? t("removeFromWatchlist") : t("addToWatchlist")}
      data-testid="watchlist-star-toggle"
      className={cn(
        STAR_BUTTON_CLASS,
        "disabled:opacity-50",
        saved ? "text-gold3" : "text-c4 hover:text-gold3",
      )}
    >
      <Star
        width={14}
        height={14}
        strokeWidth={1.5}
        fill={saved ? "currentColor" : "none"}
      />
    </button>
  );
}
