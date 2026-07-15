"use client";

import { useQuery } from "@tanstack/react-query";
import { createColumnHelper } from "@tanstack/react-table";
import { Badge, Kicker, ModerationQueue } from "@country-decision-atlas/ui";
import type { ModerationQueueAction } from "@country-decision-atlas/ui";
import {
  adminContradictionCandidatesQuery,
  useUpdateContradictionCandidateStatusMutation,
} from "../../entities/admin-contradiction-candidates/api";
import type { ContradictionCandidate } from "../../shared/api/admin-contradiction-candidates";
import { isApiError } from "../../shared/api/http";
import { ADMIN_ROLES } from "../../shared/auth/roles";
import { useAuthGuard } from "../../shared/auth/useAuthGuard";
import { routes } from "../../shared/lib/routes";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";

const SEVERITY_VARIANT: Record<string, "default" | "warning" | "negative"> = {
  low: "default",
  medium: "warning",
  high: "negative",
  critical: "negative",
};

const columnHelper = createColumnHelper<ContradictionCandidate>();

const columns = [
  columnHelper.accessor("topic", { header: "Тема" }),
  columnHelper.accessor("country_slug", {
    header: "Страна",
    cell: (info) => info.getValue() ?? "—",
  }),
  columnHelper.accessor("severity", {
    header: "Серьёзность",
    cell: (info) => (
      <Badge variant={SEVERITY_VARIANT[info.getValue()] ?? "default"}>
        {info.getValue()}
      </Badge>
    ),
  }),
  columnHelper.accessor("status", {
    header: "Статус",
    cell: (info) => <Badge variant="default">{info.getValue()}</Badge>,
  }),
];

export function ContradictionCandidatesAdminView() {
  const { status } = useAuthGuard(ADMIN_ROLES);
  const candidates = useQuery({
    ...adminContradictionCandidatesQuery("needs_review"),
    enabled: status === "ok",
  });
  const updateStatus = useUpdateContradictionCandidateStatusMutation();

  if (status === "loading" || (status === "ok" && candidates.isPending)) {
    return <LoadingState message="Загрузка кандидатов на противоречие…" />;
  }

  if (status !== "ok") {
    return (
      <ErrorState
        error="Недостаточно прав для модерации противоречий."
        backHref={routes.login}
        backLabel="Войти"
      />
    );
  }

  if (candidates.isError || !candidates.data) {
    return (
      <ErrorState
        error={isApiError(candidates.error) ? candidates.error : undefined}
      />
    );
  }

  const actions: ModerationQueueAction<ContradictionCandidate>[] = [
    {
      key: "confirm",
      label: "Подтвердить",
      onRun: (row) =>
        updateStatus.mutateAsync({
          candidateId: row.id,
          payload: { status: "confirmed" },
        }),
      successMessage: (row) => `Противоречие «${row.topic}» подтверждено.`,
    },
    {
      key: "dismiss",
      label: "Отклонить",
      variant: "dangerous",
      onRun: (row) =>
        updateStatus.mutateAsync({
          candidateId: row.id,
          payload: { status: "dismissed" },
        }),
      successMessage: (row) => `Противоречие «${row.topic}» отклонено.`,
    },
    {
      key: "archive",
      label: "Архивировать",
      variant: "dangerous",
      onRun: (row) =>
        updateStatus.mutateAsync({
          candidateId: row.id,
          payload: { status: "archived" },
        }),
      successMessage: (row) => `Противоречие «${row.topic}» архивировано.`,
    },
  ];

  return (
    <div className="flex flex-col gap-4">
      <Kicker>Кандидаты на противоречие ({candidates.data.total})</Kicker>
      <ModerationQueue
        testId="contradiction-candidates-admin"
        columns={columns}
        data={candidates.data.items}
        getRowId={(row) => row.id}
        actions={actions}
        detailTitle={(row) => row.topic}
        renderDetail={(row) => (
          <div className="flex flex-col gap-3 text-sm">
            <p className="text-c3">{row.summary}</p>
            <div>
              <span className="font-mono text-c4 text-[9px] tracking-[0.2em] uppercase">
                Утверждение A
              </span>
              <p className="text-c2 mt-1">{row.claim_a}</p>
            </div>
            <div>
              <span className="font-mono text-c4 text-[9px] tracking-[0.2em] uppercase">
                Утверждение B
              </span>
              <p className="text-c2 mt-1">{row.claim_b}</p>
            </div>
          </div>
        )}
        emptyMessage="Нет кандидатов на противоречие."
      />
    </div>
  );
}
