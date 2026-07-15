"use client";

import { useQuery } from "@tanstack/react-query";
import { createColumnHelper } from "@tanstack/react-table";
import { Badge, Kicker, ModerationQueue } from "@country-decision-atlas/ui";
import type { ModerationQueueAction } from "@country-decision-atlas/ui";
import {
  adminAuthorMetricsQuery,
  useApproveAdminAuthorMetricMutation,
  useRejectAdminAuthorMetricMutation,
} from "../../entities/author-metrics/api";
import type { AdminAuthorMetricDefinition } from "../../shared/api/author-metrics";
import { isApiError } from "../../shared/api/http";
import { ADMIN_ROLES } from "../../shared/auth/roles";
import { useAuthGuard } from "../../shared/auth/useAuthGuard";
import { routes } from "../../shared/lib/routes";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";

const columnHelper = createColumnHelper<AdminAuthorMetricDefinition>();

const columns = [
  columnHelper.accessor("slug", { header: "Slug" }),
  columnHelper.accessor("name_ru", { header: "Название" }),
  columnHelper.accessor("author.display_name", {
    header: "Автор",
    cell: (info) => info.getValue() ?? info.row.original.author_user_id,
  }),
  columnHelper.accessor("status", {
    header: "Статус",
    cell: (info) => <Badge variant="default">{info.getValue()}</Badge>,
  }),
  columnHelper.accessor("version", { header: "Версия" }),
];

export function AuthorMetricsModerationView() {
  const { status } = useAuthGuard(ADMIN_ROLES);
  const metrics = useQuery({
    ...adminAuthorMetricsQuery("review"),
    enabled: status === "ok",
  });
  const approve = useApproveAdminAuthorMetricMutation();
  const reject = useRejectAdminAuthorMetricMutation();

  if (status === "loading" || (status === "ok" && metrics.isPending)) {
    return <LoadingState message="Загрузка очереди авторских метрик…" />;
  }

  if (status !== "ok") {
    return (
      <ErrorState
        error="Недостаточно прав для модерации."
        backHref={routes.login}
        backLabel="Войти"
      />
    );
  }

  if (metrics.isError || !metrics.data) {
    return (
      <ErrorState
        error={isApiError(metrics.error) ? metrics.error : undefined}
      />
    );
  }

  const actions: ModerationQueueAction<AdminAuthorMetricDefinition>[] = [
    {
      key: "approve",
      label: "Одобрить",
      onRun: (row) => approve.mutateAsync(row.id),
      successMessage: (row) => `Метрика «${row.slug}» одобрена.`,
    },
    {
      key: "reject",
      label: "Отклонить",
      variant: "dangerous",
      requiresReason: true,
      onRun: (row, reason) =>
        reject.mutateAsync({
          definitionId: row.id,
          payload: { moderation_reason: reason },
        }),
      successMessage: (row) => `Метрика «${row.slug}» отклонена.`,
    },
  ];

  return (
    <div className="flex flex-col gap-4">
      <Kicker>Авторские метрики на модерации ({metrics.data.total})</Kicker>
      <ModerationQueue
        testId="author-metrics-moderation"
        columns={columns}
        data={metrics.data.items}
        getRowId={(row) => row.id}
        actions={actions}
        detailTitle={(row) => row.slug}
        renderDetail={(row) => (
          <div className="flex flex-col gap-3 text-sm">
            <p className="text-c3">{row.methodology_ru}</p>
            <p className="text-c4 text-xs">
              Шкала: {row.scale_min} – {row.scale_max} · Полярность:{" "}
              {row.polarity}
            </p>
            <p className="text-c4 text-xs">Лицензия: {row.license}</p>
          </div>
        )}
        emptyMessage="Нет метрик, ожидающих модерации."
      />
    </div>
  );
}
