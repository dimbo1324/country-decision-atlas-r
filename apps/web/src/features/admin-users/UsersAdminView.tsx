"use client";

import { useQuery } from "@tanstack/react-query";
import { createColumnHelper } from "@tanstack/react-table";
import {
  Badge,
  Button,
  Kicker,
  ModerationQueue,
  toast,
} from "@country-decision-atlas/ui";
import type { ModerationQueueAction } from "@country-decision-atlas/ui";
import {
  adminUsersQuery,
  useRevokeAllUserSessionsMutation,
  useUpdateUserRoleMutation,
  useUpdateUserStatusMutation,
  userSessionsQuery,
} from "../../entities/admin-users/api";
import type { AdminUser } from "../../shared/api/admin-users";
import { isApiError } from "../../shared/api/http";
import { STRICT_ADMIN_ROLES } from "../../shared/auth/roles";
import { useAuthGuard } from "../../shared/auth/useAuthGuard";
import { routes } from "../../shared/lib/routes";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";
import { formatDateTime } from "../../shared/lib/format";

const selectClass =
  "border-warm bg-bg2 text-c2 focus-visible:border-gold w-full border px-3 py-2 text-sm outline-none";

const ROLES = ["user", "editor", "moderator", "admin", "owner"] as const;

const columnHelper = createColumnHelper<AdminUser>();

const columns = [
  columnHelper.accessor("email", { header: "Email" }),
  columnHelper.accessor("display_name", { header: "Имя" }),
  columnHelper.accessor("role", {
    header: "Роль",
    cell: (info) => <Badge variant="default">{info.getValue()}</Badge>,
  }),
  columnHelper.accessor("status", {
    header: "Статус",
    cell: (info) => (
      <Badge variant={info.getValue() === "active" ? "positive" : "warning"}>
        {info.getValue()}
      </Badge>
    ),
  }),
];

function UserDetailPanel({ user }: { user: AdminUser }) {
  const sessions = useQuery(userSessionsQuery(user.id));
  const updateRole = useUpdateUserRoleMutation();
  const revokeAll = useRevokeAllUserSessionsMutation();

  async function handleRoleChange(role: (typeof ROLES)[number]) {
    try {
      await updateRole.mutateAsync({ userId: user.id, payload: { role } });
      toast.success(`Роль пользователя обновлена: ${role}.`);
    } catch (err: unknown) {
      toast.error(
        isApiError(err)
          ? (err.error?.message ?? "Не удалось обновить роль.")
          : "Не удалось обновить роль.",
      );
    }
  }

  async function handleRevokeAll() {
    try {
      const result = await revokeAll.mutateAsync(user.id);
      toast.success(`Отозвано сессий: ${result.revoked_count}.`);
    } catch (err: unknown) {
      toast.error(
        isApiError(err)
          ? (err.error?.message ?? "Не удалось отозвать сессии.")
          : "Не удалось отозвать сессии.",
      );
    }
  }

  return (
    <div className="flex flex-col gap-5 text-sm">
      <div className="flex flex-col gap-2">
        <span className="font-mono text-c4 text-[9px] tracking-[0.2em] uppercase">
          Роль
        </span>
        <select
          className={selectClass}
          value={user.role}
          onChange={(event) =>
            void handleRoleChange(event.target.value as (typeof ROLES)[number])
          }
          disabled={updateRole.isPending}
          data-testid="admin-user-role-select"
        >
          {ROLES.map((role) => (
            <option
              key={role}
              value={role}
            >
              {role}
            </option>
          ))}
        </select>
      </div>

      <div className="flex flex-col gap-2">
        <span className="font-mono text-c4 text-[9px] tracking-[0.2em] uppercase">
          Сессии
        </span>
        {sessions.isPending ? (
          <p className="text-c3">Загрузка…</p>
        ) : (sessions.data?.items ?? []).length === 0 ? (
          <p className="text-c3">Активных сессий нет.</p>
        ) : (
          <ul className="flex flex-col gap-1.5">
            {(sessions.data?.items ?? []).map((session) => (
              <li
                key={session.id}
                className="text-c3 text-xs"
              >
                {session.id.slice(0, 8)}… ·{" "}
                {session.revoked_at ? "отозвана" : "активна"} · истекает{" "}
                {formatDateTime(session.expires_at)}
              </li>
            ))}
          </ul>
        )}
        <Button
          type="button"
          variant="ghost"
          className="text-terra3 border-terra2/60"
          onClick={() => void handleRevokeAll()}
          disabled={revokeAll.isPending}
          data-testid="admin-user-revoke-all"
        >
          Отозвать все сессии
        </Button>
      </div>
    </div>
  );
}

export function UsersAdminView() {
  const { status } = useAuthGuard(STRICT_ADMIN_ROLES);
  const users = useQuery({
    ...adminUsersQuery(),
    enabled: status === "ok",
  });
  const updateStatus = useUpdateUserStatusMutation();

  if (status === "loading" || (status === "ok" && users.isPending)) {
    return <LoadingState message="Загрузка пользователей…" />;
  }

  if (status !== "ok") {
    return (
      <ErrorState
        error="Недостаточно прав для управления пользователями."
        backHref={routes.login}
        backLabel="Войти"
      />
    );
  }

  if (users.isError || !users.data) {
    return (
      <ErrorState error={isApiError(users.error) ? users.error : undefined} />
    );
  }

  const actions: ModerationQueueAction<AdminUser>[] = [
    {
      key: "suspend",
      label: "Заблокировать",
      variant: "dangerous",
      isVisible: (row) => row.status === "active",
      onRun: (row) =>
        updateStatus.mutateAsync({
          userId: row.id,
          payload: { status: "suspended" },
        }),
      successMessage: (row) => `Пользователь ${row.email} заблокирован.`,
    },
    {
      key: "reactivate",
      label: "Разблокировать",
      isVisible: (row) => row.status === "suspended",
      onRun: (row) =>
        updateStatus.mutateAsync({
          userId: row.id,
          payload: { status: "active" },
        }),
      successMessage: (row) => `Пользователь ${row.email} разблокирован.`,
    },
  ];

  return (
    <div className="flex flex-col gap-4">
      <Kicker>Пользователи ({users.data.total})</Kicker>
      <ModerationQueue
        testId="admin-users"
        columns={columns}
        data={users.data.items ?? []}
        getRowId={(row) => row.id}
        actions={actions}
        detailTitle={(row) => row.email}
        renderDetail={(row) => <UserDetailPanel user={row} />}
        emptyMessage="Нет пользователей."
      />
    </div>
  );
}
