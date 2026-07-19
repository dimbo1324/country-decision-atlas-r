"use client";

import { useTranslations } from "next-intl";
import { Badge, Button, toast } from "@country-decision-atlas/ui";
import {
  exportTrip,
  useDisableShareMutation,
  useEnableShareMutation,
} from "../../entities/trips/api";
import type { TripDetail } from "../../shared/api/trips";
import { isApiError } from "../../shared/api/http";
import { routes } from "../../shared/lib/routes";

export function TripShareExport({ trip }: { trip: TripDetail }) {
  const t = useTranslations("tripShareExport");
  const enableShare = useEnableShareMutation(trip.id);
  const disableShare = useDisableShareMutation(trip.id);
  const isShared = trip.visibility === "link";

  async function handleEnableShare() {
    try {
      const result = await enableShare.mutateAsync();
      const url = `${window.location.origin}${routes.tripSharedPublic(result.token)}`;
      await navigator.clipboard.writeText(url).catch(() => undefined);
      toast.success(t("linkCreated"));
    } catch (err: unknown) {
      toast.error(
        isApiError(err)
          ? (err.error?.message ?? t("linkCreateError"))
          : t("linkCreateError"),
      );
    }
  }

  async function handleDisableShare() {
    try {
      await disableShare.mutateAsync();
      toast.success(t("linkDisabled"));
    } catch (err: unknown) {
      toast.error(
        isApiError(err)
          ? (err.error?.message ?? t("linkDisableError"))
          : t("linkDisableError"),
      );
    }
  }

  async function handleExport() {
    try {
      const data = await exportTrip(trip.id);
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `trip-${trip.id}.json`;
      anchor.click();
      URL.revokeObjectURL(url);
    } catch (err: unknown) {
      toast.error(
        isApiError(err)
          ? (err.error?.message ?? t("exportError"))
          : t("exportError"),
      );
    }
  }

  return (
    <div
      className="flex flex-wrap items-center gap-3"
      data-testid="trip-share-export"
    >
      <Badge variant="default">
        {isShared ? t("availableByLink") : t("private")}
      </Badge>
      {isShared ? (
        <Button
          variant="ghost"
          onClick={handleDisableShare}
          disabled={disableShare.isPending}
          data-testid="trip-share-disable"
        >
          {t("disableLink")}
        </Button>
      ) : (
        <Button
          variant="ghost"
          onClick={handleEnableShare}
          disabled={enableShare.isPending}
          data-testid="trip-share-enable"
        >
          {t("createPublicLink")}
        </Button>
      )}
      <Button
        variant="ghost"
        onClick={handleExport}
        data-testid="trip-export-button"
      >
        {t("export")}
      </Button>
    </div>
  );
}
