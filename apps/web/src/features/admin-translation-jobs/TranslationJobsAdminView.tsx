"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { createColumnHelper } from "@tanstack/react-table";
import {
  Badge,
  Button,
  Card,
  Field,
  FieldLabel,
  Kicker,
  ModerationQueue,
  toast,
} from "@country-decision-atlas/ui";
import {
  adminTranslationJobsQuery,
  useCreateMissingTranslationJobsMutation,
  useCreateStaleTranslationJobsMutation,
  useProcessTranslationJobBatchMutation,
  useRetryFailedTranslationJobsMutation,
} from "../../entities/admin-translation-jobs/api";
import type { TranslationJobItem } from "../../shared/api/admin-translation-jobs";
import { isApiError } from "../../shared/api/http";
import { ADMIN_ROLES } from "../../shared/auth/roles";
import { useAuthGuard } from "../../shared/auth/useAuthGuard";
import { routes } from "../../shared/lib/routes";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";

const inputClass =
  "border-warm bg-bg2 text-c1 font-body border px-3 py-2 text-sm outline-none focus-visible:border-gold transition-colors duration-200 w-24";
const selectClass =
  "border-warm bg-bg2 text-c2 focus-visible:border-gold border px-3 py-2 text-sm outline-none";

const columnHelper = createColumnHelper<TranslationJobItem>();

const columns = [
  columnHelper.accessor("target_locale_code", {
    header: "Локаль",
    cell: (info) => info.getValue() ?? "—",
  }),
  columnHelper.accessor("status", {
    header: "Статус",
    cell: (info) => <Badge variant="default">{info.getValue()}</Badge>,
  }),
  columnHelper.accessor("priority", { header: "Приоритет" }),
];

function BatchActionCard({
  title,
  onRun,
  pending,
  children,
  testId,
}: {
  title: string;
  onRun: () => void;
  pending: boolean;
  children?: React.ReactNode;
  testId: string;
}) {
  return (
    <Card
      interactive={false}
      className="flex flex-col gap-3"
    >
      <Kicker>{title}</Kicker>
      <div className="flex flex-wrap items-end gap-3">
        {children}
        <Button
          type="button"
          onClick={onRun}
          disabled={pending}
          data-testid={testId}
        >
          Запустить
        </Button>
      </div>
    </Card>
  );
}

export function TranslationJobsAdminView() {
  const { status } = useAuthGuard(ADMIN_ROLES);
  const jobs = useQuery({
    ...adminTranslationJobsQuery(),
    enabled: status === "ok",
  });

  const createMissing = useCreateMissingTranslationJobsMutation();
  const createStale = useCreateStaleTranslationJobsMutation();
  const processBatch = useProcessTranslationJobBatchMutation();
  const retryFailed = useRetryFailedTranslationJobsMutation();

  const [locale, setLocale] = useState<"ru" | "en">("ru");
  const [limit, setLimit] = useState(50);

  async function runAction<T>(
    mutateAsync: () => Promise<T>,
    successMessage: string,
  ) {
    try {
      await mutateAsync();
      toast.success(successMessage);
    } catch (err: unknown) {
      toast.error(
        isApiError(err)
          ? (err.error?.message ?? "Действие не выполнено.")
          : "Действие не выполнено.",
      );
    }
  }

  if (status === "loading" || (status === "ok" && jobs.isPending)) {
    return <LoadingState message="Загрузка очереди переводов…" />;
  }

  if (status !== "ok") {
    return (
      <ErrorState
        error="Недостаточно прав для управления переводами."
        backHref={routes.login}
        backLabel="Войти"
      />
    );
  }

  if (jobs.isError || !jobs.data) {
    return (
      <ErrorState error={isApiError(jobs.error) ? jobs.error : undefined} />
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-end gap-3">
        <Field>
          <FieldLabel htmlFor="tj-locale">Локаль</FieldLabel>
          <select
            id="tj-locale"
            className={selectClass}
            value={locale}
            onChange={(event) => setLocale(event.target.value as "ru" | "en")}
            data-testid="translation-jobs-locale-select"
          >
            <option value="ru">ru</option>
            <option value="en">en</option>
          </select>
        </Field>
        <Field>
          <FieldLabel htmlFor="tj-limit">Лимит</FieldLabel>
          <input
            id="tj-limit"
            type="number"
            className={inputClass}
            value={limit}
            onChange={(event) => setLimit(Number(event.target.value))}
            data-testid="translation-jobs-limit-input"
          />
        </Field>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <BatchActionCard
          title="Создать недостающие"
          pending={createMissing.isPending}
          testId="translation-jobs-create-missing"
          onRun={() =>
            void runAction(
              () =>
                createMissing.mutateAsync({
                  target_locale: locale,
                  limit,
                  priority: 0,
                }),
              "Задачи на перевод созданы.",
            )
          }
        />
        <BatchActionCard
          title="Создать устаревшие"
          pending={createStale.isPending}
          testId="translation-jobs-create-stale"
          onRun={() =>
            void runAction(
              () =>
                createStale.mutateAsync({
                  target_locale: locale,
                  limit,
                  priority: 0,
                }),
              "Задачи на обновление перевода созданы.",
            )
          }
        />
        <BatchActionCard
          title="Обработать пачку"
          pending={processBatch.isPending}
          testId="translation-jobs-process-batch"
          onRun={() =>
            void runAction(
              () =>
                processBatch.mutateAsync({
                  target_locale: locale,
                  limit,
                  worker_id: "internal-console",
                  dry_run: false,
                }),
              "Пачка задач обработана.",
            )
          }
        />
        <BatchActionCard
          title="Повторить неудачные"
          pending={retryFailed.isPending}
          testId="translation-jobs-retry-failed"
          onRun={() =>
            void runAction(
              () => retryFailed.mutateAsync({ target_locale: locale, limit }),
              "Неудачные задачи возвращены в очередь.",
            )
          }
        />
      </div>

      <div className="flex flex-col gap-4">
        <Kicker>Задачи ({jobs.data.pagination.total})</Kicker>
        <ModerationQueue
          testId="translation-jobs-admin"
          columns={columns}
          data={jobs.data.items}
          getRowId={(row) => row.id}
          actions={[]}
          emptyMessage="Нет задач на перевод."
        />
      </div>
    </div>
  );
}
