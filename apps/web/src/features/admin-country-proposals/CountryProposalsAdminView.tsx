"use client";

import { useQuery } from "@tanstack/react-query";
import { createColumnHelper } from "@tanstack/react-table";
import { Badge, Kicker, ModerationQueue } from "@country-decision-atlas/ui";
import type { ModerationQueueAction } from "@country-decision-atlas/ui";
import {
  adminCountryProposalsQuery,
  useArchiveProposalMutation,
  useAssignCuratorMutation,
  usePublishProposalMutation,
  useReadinessCheckMutation,
  useRejectProposalMutation,
  useRequestChangesMutation,
} from "../../entities/admin-country-proposals/api";
import type { CountryProposal } from "../../shared/api/admin-country-proposals";
import { isApiError } from "../../shared/api/http";
import { ADMIN_ROLES } from "../../shared/auth/roles";
import { useAuthGuard } from "../../shared/auth/useAuthGuard";
import { routes } from "../../shared/lib/routes";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";

const columnHelper = createColumnHelper<CountryProposal>();

const columns = [
  columnHelper.accessor("slug", { header: "Slug" }),
  columnHelper.accessor("name_ru", { header: "Название" }),
  columnHelper.accessor("status", {
    header: "Статус",
    cell: (info) => <Badge variant="default">{info.getValue()}</Badge>,
  }),
  columnHelper.accessor("curator_user_id", {
    header: "Куратор",
    cell: (info) => info.getValue() ?? "—",
  }),
];

export function CountryProposalsAdminView() {
  const { status } = useAuthGuard(ADMIN_ROLES);
  const proposals = useQuery({
    ...adminCountryProposalsQuery(),
    enabled: status === "ok",
  });

  const assignCurator = useAssignCuratorMutation();
  const readinessCheck = useReadinessCheckMutation();
  const publish = usePublishProposalMutation();
  const reject = useRejectProposalMutation();
  const requestChanges = useRequestChangesMutation();
  const archive = useArchiveProposalMutation();

  if (status === "loading" || (status === "ok" && proposals.isPending)) {
    return <LoadingState message="Загрузка заявок стран…" />;
  }

  if (status !== "ok") {
    return (
      <ErrorState
        error="Недостаточно прав для управления заявками стран."
        backHref={routes.login}
        backLabel="Войти"
      />
    );
  }

  if (proposals.isError || !proposals.data) {
    return (
      <ErrorState
        error={isApiError(proposals.error) ? proposals.error : undefined}
      />
    );
  }

  const actions: ModerationQueueAction<CountryProposal>[] = [
    {
      key: "assign-curator",
      label: "Назначить себя куратором",
      isVisible: (row) => !row.curator_user_id,
      onRun: (row) => assignCurator.mutateAsync(row.id),
      successMessage: (row) => `Куратор для «${row.slug}» назначен.`,
    },
    {
      key: "readiness-check",
      label: "Проверить готовность",
      onRun: (row) => readinessCheck.mutateAsync(row.id),
      successMessage: (row) => `Проверка готовности «${row.slug}» выполнена.`,
    },
    {
      key: "publish",
      label: "Опубликовать",
      variant: "dangerous",
      onRun: (row) => publish.mutateAsync(row.id),
      successMessage: (row) => `Заявка «${row.slug}» опубликована.`,
    },
    {
      key: "request-changes",
      label: "Запросить правки",
      variant: "dangerous",
      requiresReason: true,
      onRun: (row, reason) =>
        requestChanges.mutateAsync({
          proposalId: row.id,
          payload: { reason: reason ?? "" },
        }),
      successMessage: (row) => `Правки для «${row.slug}» запрошены.`,
    },
    {
      key: "reject",
      label: "Отклонить",
      variant: "dangerous",
      requiresReason: true,
      onRun: (row, reason) =>
        reject.mutateAsync({
          proposalId: row.id,
          payload: { reason: reason ?? "" },
        }),
      successMessage: (row) => `Заявка «${row.slug}» отклонена.`,
    },
    {
      key: "archive",
      label: "Архивировать",
      variant: "dangerous",
      onRun: (row) => archive.mutateAsync(row.id),
      successMessage: (row) => `Заявка «${row.slug}» архивирована.`,
    },
  ];

  return (
    <div className="flex flex-col gap-4">
      <Kicker>Заявки стран ({proposals.data.total})</Kicker>
      <ModerationQueue
        testId="country-proposals-admin"
        columns={columns}
        data={proposals.data.items}
        getRowId={(row) => row.id}
        actions={actions}
        detailTitle={(row) => row.slug}
        renderDetail={(row) => (
          <div className="flex flex-col gap-3 text-sm">
            <p className="text-c3">{row.justification}</p>
            <p className="text-c4 text-xs">
              ISO: {row.iso2} / {row.iso3}
            </p>
            {row.moderation_reason && (
              <p className="text-terra3 text-xs">
                Причина: {row.moderation_reason}
              </p>
            )}
            <div>
              <span className="font-mono text-c4 text-[9px] tracking-[0.2em] uppercase">
                Снимок готовности
              </span>
              <pre className="border-warm bg-bg2 text-c3 mt-2 overflow-x-auto border p-3 text-xs">
                {row.readiness_snapshot
                  ? JSON.stringify(row.readiness_snapshot, null, 2)
                  : "Проверка ещё не выполнялась."}
              </pre>
            </div>
          </div>
        )}
        emptyMessage="Нет заявок стран."
      />
    </div>
  );
}
