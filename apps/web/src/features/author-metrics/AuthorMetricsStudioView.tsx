"use client";

import { useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useQuery } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { z } from "zod";
import {
  Badge,
  Button,
  Card,
  Field,
  FieldError,
  FieldLabel,
  Kicker,
  toast,
} from "@country-decision-atlas/ui";
import {
  myAuthorMetricsQuery,
  myAuthorMetricValuesQuery,
  useArchiveAuthorMetricMutation,
  useCreateAuthorMetricMutation,
  useSubmitAuthorMetricMutation,
  useUpsertAuthorMetricValuesMutation,
} from "../../entities/author-metrics/api";
import { allCountriesQuery } from "../../entities/decision/api";
import type { MyAuthorMetricDefinition } from "../../shared/api/author-metrics";
import { isApiError } from "../../shared/api/http";
import { useAuth } from "../../shared/auth/AuthProvider";
import { useAppLocale } from "../../shared/lib/useAppLocale";
import { Link } from "../../i18n/navigation";
import { routes } from "../../shared/lib/routes";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";

const inputClass =
  "border-warm bg-bg2 text-c1 font-body border px-4 py-2.5 text-sm outline-none focus-visible:border-gold transition-colors duration-200";

const STATUS_LABELS: Record<string, string> = {
  draft: "Черновик",
  submitted: "На модерации",
  published: "Опубликована",
  rejected: "Отклонена",
  archived: "В архиве",
};

const createMetricSchema = z.object({
  slug: z
    .string()
    .min(1, "Введите slug")
    .regex(/^[a-z0-9_]+$/, "Только строчные буквы, цифры и подчёркивания"),
  nameEn: z.string().min(1, "Введите название (en)"),
  nameRu: z.string().min(1, "Введите название (ru)"),
});
type CreateMetricValues = z.infer<typeof createMetricSchema>;

function CreateMetricForm() {
  const createMetric = useCreateAuthorMetricMutation();
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<CreateMetricValues>({
    resolver: zodResolver(createMetricSchema),
  });

  async function onSubmit(values: CreateMetricValues) {
    try {
      await createMetric.mutateAsync({
        slug: values.slug,
        name_en: values.nameEn,
        name_ru: values.nameRu,
        methodology_en: "",
        methodology_ru: "",
        polarity: "higher_is_better",
        scale_min: 0,
        scale_max: 100,
        license: "platform",
        visibility: "private",
      });
      reset();
      toast.success("Метрика создана как черновик.");
    } catch (err: unknown) {
      toast.error(
        isApiError(err)
          ? (err.error?.message ?? "Не удалось создать метрику.")
          : "Не удалось создать метрику.",
      );
    }
  }

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="grid grid-cols-1 gap-4 sm:grid-cols-[1fr_1fr_1fr_auto] sm:items-end"
      noValidate
    >
      <Field>
        <FieldLabel htmlFor="metric-slug">Slug</FieldLabel>
        <input
          id="metric-slug"
          className={inputClass}
          placeholder="cost_of_living_index"
          data-testid="author-metric-slug-input"
          {...register("slug")}
        />
        <FieldError>{errors.slug?.message}</FieldError>
      </Field>
      <Field>
        <FieldLabel htmlFor="metric-name-en">Название (en)</FieldLabel>
        <input
          id="metric-name-en"
          className={inputClass}
          data-testid="author-metric-name-en-input"
          {...register("nameEn")}
        />
        <FieldError>{errors.nameEn?.message}</FieldError>
      </Field>
      <Field>
        <FieldLabel htmlFor="metric-name-ru">Название (ru)</FieldLabel>
        <input
          id="metric-name-ru"
          className={inputClass}
          data-testid="author-metric-name-ru-input"
          {...register("nameRu")}
        />
        <FieldError>{errors.nameRu?.message}</FieldError>
      </Field>
      <Button
        type="submit"
        disabled={createMetric.isPending}
        data-testid="author-metric-create-submit"
      >
        Создать
      </Button>
    </form>
  );
}

function MetricValuesEditor({ metric }: { metric: MyAuthorMetricDefinition }) {
  const locale = useAppLocale();
  const countries = useQuery(allCountriesQuery(locale));
  const values = useQuery(myAuthorMetricValuesQuery(metric.id));
  const upsertValues = useUpsertAuthorMetricValuesMutation(metric.id);
  const [draftValues, setDraftValues] = useState<Record<string, string>>({});

  const existingBySlug = new Map(
    (values.data?.items ?? []).map((item) => [item.country_slug, item]),
  );

  async function handleSave() {
    const items = Object.entries(draftValues)
      .filter(([, raw]) => raw.trim() !== "")
      .map(([countrySlug, raw]) => ({
        country_slug: countrySlug,
        value: Number(raw),
        is_personal_experience: false,
      }));
    if (items.length === 0) return;
    try {
      await upsertValues.mutateAsync(items);
      setDraftValues({});
      toast.success("Значения сохранены.");
    } catch (err: unknown) {
      toast.error(
        isApiError(err)
          ? (err.error?.message ?? "Не удалось сохранить значения.")
          : "Не удалось сохранить значения.",
      );
    }
  }

  return (
    <div
      className="flex flex-col gap-3"
      data-testid="author-metric-values-editor"
    >
      {(countries.data?.items ?? []).map((country) => {
        const existing = existingBySlug.get(country.slug);
        return (
          <div
            key={country.slug}
            className="flex items-center gap-3"
          >
            <span className="text-c3 w-32 text-sm">{country.name}</span>
            <input
              type="number"
              className={inputClass}
              placeholder={
                existing
                  ? String(existing.value)
                  : `${metric.scale_min}-${metric.scale_max}`
              }
              value={draftValues[country.slug] ?? ""}
              onChange={(event) =>
                setDraftValues((current) => ({
                  ...current,
                  [country.slug]: event.target.value,
                }))
              }
              data-testid={`author-metric-value-${country.slug}`}
            />
          </div>
        );
      })}
      <Button
        variant="ghost"
        onClick={() => void handleSave()}
        disabled={upsertValues.isPending}
        data-testid="author-metric-values-save"
      >
        Сохранить значения
      </Button>
    </div>
  );
}

function MetricRow({ metric }: { metric: MyAuthorMetricDefinition }) {
  const [expanded, setExpanded] = useState(false);
  const submitMetric = useSubmitAuthorMetricMutation();
  const archiveMetric = useArchiveAuthorMetricMutation();

  return (
    <div data-testid="author-metric-row">
      <Card
        interactive={false}
        className="flex flex-col gap-3"
      >
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-col gap-1">
            <span className="font-display text-lg font-semibold">
              {metric.name_ru}
            </span>
            <span className="text-c4 font-mono text-xs">{metric.slug}</span>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="default">
              {STATUS_LABELS[metric.status] ?? metric.status}
            </Badge>
            <Button
              variant="ghost"
              onClick={() => setExpanded((current) => !current)}
            >
              {expanded ? "Скрыть значения" : "Значения по странам"}
            </Button>
            <Button
              variant="ghost"
              onClick={() => submitMetric.mutate(metric.id)}
              disabled={metric.status !== "draft" || submitMetric.isPending}
              data-testid="author-metric-submit"
            >
              На модерацию
            </Button>
            <Button
              variant="ghost"
              onClick={() => archiveMetric.mutate(metric.id)}
              disabled={metric.status === "archived" || archiveMetric.isPending}
            >
              Архив
            </Button>
          </div>
        </div>
        {expanded && <MetricValuesEditor metric={metric} />}
      </Card>
    </div>
  );
}

export function AuthorMetricsStudioView() {
  const { user, isLoading: authLoading } = useAuth();
  const metrics = useQuery({
    ...myAuthorMetricsQuery(),
    enabled: Boolean(user),
  });

  if (authLoading) {
    return <LoadingState message="Загрузка…" />;
  }

  if (!user) {
    return (
      <div
        className="border-warm flex flex-col gap-2 border px-4 py-4"
        data-testid="author-metrics-unauthenticated"
      >
        <p className="text-c3 text-sm">
          Войдите, чтобы вести студию авторских метрик.{" "}
          <Link
            href={routes.login}
            className="text-c1 hover:text-gold3 underline decoration-dotted underline-offset-2 transition-colors duration-200"
          >
            Войти
          </Link>
        </p>
      </div>
    );
  }

  return (
    <div
      className="flex flex-col gap-8"
      data-testid="author-metrics-studio"
    >
      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <Kicker>Новая метрика</Kicker>
        <CreateMetricForm />
      </Card>

      <div className="flex flex-col gap-4">
        <Kicker>Мои метрики</Kicker>
        {metrics.isPending ? (
          <LoadingState message="Загрузка метрик…" />
        ) : metrics.isError ? (
          <ErrorState
            error={isApiError(metrics.error) ? metrics.error : undefined}
          />
        ) : (metrics.data.items ?? []).length === 0 ? (
          <div data-testid="author-metrics-empty-state">
            <EmptyState message="У вас пока нет метрик." />
          </div>
        ) : (
          <div
            className="flex flex-col gap-4"
            data-testid="author-metrics-list"
          >
            {(metrics.data.items ?? []).map((metric) => (
              <MetricRow
                key={metric.id}
                metric={metric}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
