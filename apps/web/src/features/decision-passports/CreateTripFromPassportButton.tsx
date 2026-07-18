"use client";

import { useTranslations } from "next-intl";
import { Button, toast } from "@country-decision-atlas/ui";
import { Link, useRouter } from "../../i18n/navigation";
import { useCreateTripFromPassportMutation } from "../../entities/trips/api";
import { isApiError } from "../../shared/api/http";
import { useAuth } from "../../shared/auth/AuthProvider";
import { hasSessionHint } from "../../shared/auth/session";
import { routes } from "../../shared/lib/routes";

/** The plan's Stage 7 CTA: turn a saved decision passport into a trip
 * (`POST /me/trips/from-passport`) straight from the passport document. */
export function CreateTripFromPassportButton({ token }: { token: string }) {
  const t = useTranslations("decisionPassports");
  const { user, isLoading: isAuthLoading } = useAuth();
  const router = useRouter();
  const createTrip = useCreateTripFromPassportMutation();

  // Same SSR-safety rule as WatchlistButton: this page is force-dynamic,
  // so the signed-out branch must be decided without a client-only state
  // flip that would duplicate SSR content.
  if (!hasSessionHint() || (!isAuthLoading && !user)) {
    return (
      <Link
        href={routes.login}
        className="font-mono text-gold3 hover:text-gold text-[10px] tracking-[0.2em] uppercase transition-colors duration-300"
        data-testid="trip-from-passport-login-required"
      >
        {t("loginToCreateTrip")}
      </Link>
    );
  }

  if (isAuthLoading) {
    return null;
  }

  function handleCreate() {
    createTrip.mutate(
      { token },
      {
        onSuccess: (response) => {
          toast.success(t("tripCreated"));
          router.push(routes.tripDetail(response.item.id));
        },
        onError: (error) => {
          toast.error(
            isApiError(error) && error.error?.message
              ? error.error.message
              : t("tripCreateError"),
          );
        },
      },
    );
  }

  return (
    <Button
      type="button"
      onClick={handleCreate}
      disabled={createTrip.isPending}
      data-testid="trip-from-passport-button"
    >
      {createTrip.isPending ? t("creatingTrip") : t("createTripFromPassport")}
    </Button>
  );
}
