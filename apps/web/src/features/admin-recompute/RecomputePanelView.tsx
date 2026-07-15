"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import {
  Button,
  Card,
  Dialog,
  DialogContent,
  Kicker,
} from "@country-decision-atlas/ui";
import { adminRecomputeApi } from "../../shared/api/admin-recompute";
import { isApiError } from "../../shared/api/http";
import { ADMIN_ROLES } from "../../shared/auth/roles";
import { useAuthGuard } from "../../shared/auth/useAuthGuard";
import { routes } from "../../shared/lib/routes";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";

type LogEntry = {
  timestamp: string;
  resource: string;
  message: string;
};

const RESOURCES = [
  {
    key: "platform-metrics",
    label: "Метрики платформы",
    run: adminRecomputeApi.recomputeAllPlatformMetrics,
  },
  {
    key: "trust",
    label: "Доверие стран",
    run: adminRecomputeApi.recomputeAllTrust,
  },
  {
    key: "country-drift",
    label: "Дрейф стран",
    run: adminRecomputeApi.recomputeAllCountryDrift,
  },
] as const;

export function RecomputePanelView() {
  const { status } = useAuthGuard(ADMIN_ROLES);
  const [log, setLog] = useState<LogEntry[]>([]);
  const [pendingResource, setPendingResource] = useState<
    (typeof RESOURCES)[number] | null
  >(null);
  const mutation = useMutation({
    mutationFn: (
      run: () => Promise<{ resource: string; event_id?: string | null }>,
    ) => run(),
  });

  if (status === "loading") {
    return <LoadingState message="Проверка прав…" />;
  }

  if (status !== "ok") {
    return (
      <ErrorState
        error="Недостаточно прав для запуска пересчёта."
        backHref={routes.login}
        backLabel="Войти"
      />
    );
  }

  async function handleConfirm() {
    if (!pendingResource) return;
    try {
      const result = await mutation.mutateAsync(pendingResource.run);
      setLog((current) => [
        {
          timestamp: new Date().toLocaleTimeString("ru"),
          resource: pendingResource.label,
          message: `queued: event_id=${result.event_id ?? "н/д"}`,
        },
        ...current,
      ]);
    } catch (err: unknown) {
      setLog((current) => [
        {
          timestamp: new Date().toLocaleTimeString("ru"),
          resource: pendingResource.label,
          message: isApiError(err)
            ? `ошибка: ${err.error?.message ?? "неизвестно"}`
            : "ошибка: неизвестно",
        },
        ...current,
      ]);
    } finally {
      setPendingResource(null);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <Kicker>Запуск пересчёта</Kicker>
        <div className="flex flex-wrap gap-3">
          {RESOURCES.map((resource) => (
            <Button
              key={resource.key}
              type="button"
              variant="ghost"
              className="text-terra3 border-terra2/60"
              onClick={() => setPendingResource(resource)}
              data-testid={`recompute-${resource.key}`}
            >
              {resource.label}
            </Button>
          ))}
        </div>
      </Card>

      <div className="flex flex-col gap-2">
        <Kicker>Журнал</Kicker>
        {log.length === 0 ? (
          <p className="text-c4 text-sm">Пересчёты ещё не запускались.</p>
        ) : (
          <pre
            className="border-warm bg-bg2 text-c3 overflow-x-auto border p-4 text-xs leading-relaxed"
            data-testid="recompute-log"
          >
            {log
              .map(
                (entry) =>
                  `[${entry.timestamp}] ${entry.resource} — ${entry.message}`,
              )
              .join("\n")}
          </pre>
        )}
      </div>

      <Dialog
        open={pendingResource !== null}
        onOpenChange={(open) => !open && setPendingResource(null)}
      >
        {pendingResource && (
          <DialogContent
            title={`Пересчитать: ${pendingResource.label}`}
            description="Действие запустит полный пересчёт для всех стран. Подтвердите продолжение."
          >
            <div className="flex justify-end gap-2">
              <Button
                type="button"
                variant="ghost"
                onClick={() => setPendingResource(null)}
              >
                Отмена
              </Button>
              <Button
                type="button"
                disabled={mutation.isPending}
                onClick={() => void handleConfirm()}
                data-testid="recompute-confirm"
              >
                Подтвердить
              </Button>
            </div>
          </DialogContent>
        )}
      </Dialog>
    </div>
  );
}
