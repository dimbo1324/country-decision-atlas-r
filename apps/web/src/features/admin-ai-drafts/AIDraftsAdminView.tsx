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
import type { ModerationQueueAction } from "@country-decision-atlas/ui";
import {
  adminAiDraftsQuery,
  useGenerateAiDraftSummaryMutation,
  useUpdateAiDraftStatusMutation,
} from "../../entities/admin-ai-drafts/api";
import type { AIDraft } from "../../shared/api/admin-ai-drafts";
import { isApiError } from "../../shared/api/http";
import { ADMIN_ROLES } from "../../shared/auth/roles";
import { useAuthGuard } from "../../shared/auth/useAuthGuard";
import { routes } from "../../shared/lib/routes";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";

const inputClass =
  "border-warm bg-bg2 text-c1 font-body border px-4 py-2.5 text-sm outline-none focus-visible:border-gold transition-colors duration-200";

const columnHelper = createColumnHelper<AIDraft>();

const columns = [
  columnHelper.accessor("title", { header: "Заголовок" }),
  columnHelper.accessor("draft_type", { header: "Тип" }),
  columnHelper.accessor("confidence", {
    header: "Уверенность",
    cell: (info) => <Badge variant="default">{info.getValue()}</Badge>,
  }),
  columnHelper.accessor("status", {
    header: "Статус",
    cell: (info) => <Badge variant="default">{info.getValue()}</Badge>,
  }),
];

function GenerateSummaryForm() {
  const generate = useGenerateAiDraftSummaryMutation();
  const [topic, setTopic] = useState("");
  const [countrySlug, setCountrySlug] = useState("");

  async function handleGenerate() {
    if (!topic.trim()) return;
    try {
      await generate.mutateAsync({
        topic,
        country_slug: countrySlug || undefined,
        locale: "ru",
      });
      toast.success("Черновик сгенерирован.");
      setTopic("");
      setCountrySlug("");
    } catch (err: unknown) {
      toast.error(
        isApiError(err)
          ? (err.error?.message ?? "Не удалось сгенерировать черновик.")
          : "Не удалось сгенерировать черновик.",
      );
    }
  }

  return (
    <Card
      interactive={false}
      className="flex flex-col gap-4"
    >
      <Kicker>Сгенерировать сводку</Kicker>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-[2fr_1fr_auto] sm:items-end">
        <Field>
          <FieldLabel htmlFor="draft-topic">Тема</FieldLabel>
          <input
            id="draft-topic"
            className={inputClass}
            value={topic}
            onChange={(event) => setTopic(event.target.value)}
            data-testid="ai-draft-topic-input"
          />
        </Field>
        <Field>
          <FieldLabel htmlFor="draft-country">Страна (slug)</FieldLabel>
          <input
            id="draft-country"
            className={inputClass}
            value={countrySlug}
            onChange={(event) => setCountrySlug(event.target.value)}
            data-testid="ai-draft-country-input"
          />
        </Field>
        <Button
          type="button"
          onClick={() => void handleGenerate()}
          disabled={generate.isPending || !topic.trim()}
          data-testid="ai-draft-generate"
        >
          Сгенерировать
        </Button>
      </div>
    </Card>
  );
}

export function AIDraftsAdminView() {
  const { status } = useAuthGuard(ADMIN_ROLES);
  const drafts = useQuery({
    ...adminAiDraftsQuery("needs_review"),
    enabled: status === "ok",
  });
  const updateStatus = useUpdateAiDraftStatusMutation();

  if (status === "loading" || (status === "ok" && drafts.isPending)) {
    return <LoadingState message="Загрузка AI-черновиков…" />;
  }

  if (status !== "ok") {
    return (
      <ErrorState
        error="Недостаточно прав для модерации AI-черновиков."
        backHref={routes.login}
        backLabel="Войти"
      />
    );
  }

  if (drafts.isError || !drafts.data) {
    return (
      <ErrorState error={isApiError(drafts.error) ? drafts.error : undefined} />
    );
  }

  const actions: ModerationQueueAction<AIDraft>[] = [
    {
      key: "approve",
      label: "Одобрить",
      onRun: (row) =>
        updateStatus.mutateAsync({
          draftId: row.id,
          payload: { status: "approved" },
        }),
      successMessage: (row) => `Черновик «${row.title}» одобрен.`,
    },
    {
      key: "reject",
      label: "Отклонить",
      variant: "dangerous",
      onRun: (row) =>
        updateStatus.mutateAsync({
          draftId: row.id,
          payload: { status: "rejected" },
        }),
      successMessage: (row) => `Черновик «${row.title}» отклонён.`,
    },
    {
      key: "archive",
      label: "Архивировать",
      variant: "dangerous",
      onRun: (row) =>
        updateStatus.mutateAsync({
          draftId: row.id,
          payload: { status: "archived" },
        }),
      successMessage: (row) => `Черновик «${row.title}» архивирован.`,
    },
  ];

  return (
    <div className="flex flex-col gap-6">
      <GenerateSummaryForm />
      <div className="flex flex-col gap-4">
        <Kicker>Черновики на модерации ({drafts.data.total})</Kicker>
        <ModerationQueue
          testId="ai-drafts-admin"
          columns={columns}
          data={drafts.data.items}
          getRowId={(row) => row.id}
          actions={actions}
          detailTitle={(row) => row.title}
          renderDetail={(row) => (
            <div className="flex flex-col gap-3 text-sm">
              {row.summary && <p className="text-c3">{row.summary}</p>}
              <p className="text-c2 leading-relaxed">{row.body}</p>
              <p className="text-c4 text-xs">
                {row.provider} · {row.model_name} ({row.model_version})
              </p>
            </div>
          )}
          emptyMessage="Нет черновиков, ожидающих модерации."
        />
      </div>
    </div>
  );
}
