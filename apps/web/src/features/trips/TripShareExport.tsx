"use client";

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
  const enableShare = useEnableShareMutation(trip.id);
  const disableShare = useDisableShareMutation(trip.id);
  const isShared = trip.visibility === "link";

  async function handleEnableShare() {
    try {
      const result = await enableShare.mutateAsync();
      const url = `${window.location.origin}${routes.tripSharedPublic(result.token)}`;
      await navigator.clipboard.writeText(url).catch(() => undefined);
      toast.success("Публичная ссылка создана и скопирована.");
    } catch (err: unknown) {
      toast.error(
        isApiError(err)
          ? (err.error?.message ?? "Не удалось создать ссылку.")
          : "Не удалось создать ссылку.",
      );
    }
  }

  async function handleDisableShare() {
    try {
      await disableShare.mutateAsync();
      toast.success("Публичная ссылка отключена.");
    } catch (err: unknown) {
      toast.error(
        isApiError(err)
          ? (err.error?.message ?? "Не удалось отключить ссылку.")
          : "Не удалось отключить ссылку.",
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
          ? (err.error?.message ?? "Не удалось экспортировать поездку.")
          : "Не удалось экспортировать поездку.",
      );
    }
  }

  return (
    <div
      className="flex flex-wrap items-center gap-3"
      data-testid="trip-share-export"
    >
      <Badge variant="default">
        {isShared ? "Доступна по ссылке" : "Приватная"}
      </Badge>
      {isShared ? (
        <Button
          variant="ghost"
          onClick={handleDisableShare}
          disabled={disableShare.isPending}
          data-testid="trip-share-disable"
        >
          Отключить ссылку
        </Button>
      ) : (
        <Button
          variant="ghost"
          onClick={handleEnableShare}
          disabled={enableShare.isPending}
          data-testid="trip-share-enable"
        >
          Создать публичную ссылку
        </Button>
      )}
      <Button
        variant="ghost"
        onClick={handleExport}
        data-testid="trip-export-button"
      >
        Экспортировать
      </Button>
    </div>
  );
}
