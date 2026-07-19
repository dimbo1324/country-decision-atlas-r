"use client";

import { useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useQuery } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
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
import { toApiLocale } from "../../shared/lib/locale";
import { moderationStatusLabel } from "../../shared/lib/moderation-status-labels";
import { Link } from "../../i18n/navigation";
import { routes } from "../../shared/lib/routes";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";

const inputClass =
  "border-warm bg-bg2 text-c1 font-body border px-4 py-2.5 text-sm outline-none focus-visible:border-gold transition-colors duration-200";

function CreateMetricForm() {
  const t = useTranslations("authorMetricsStudio");
  const createMetric = useCreateAuthorMetricMutation();

  const createMetricSchema = z.object({
    slug: z
      .string()
      .min(1, t("slugRequired"))
      .regex(/^[a-z0-9_]+$/, t("slugPattern")),
    nameEn: z.string().min(1, t("nameEnRequired")),
    nameRu: z.string().min(1, t("nameRuRequired")),
  });
  type CreateMetricValues = z.infer<typeof createMetricSchema>;

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
      toast.success(t("metricCreatedToast"));
    } catch (err: unknown) {
      toast.error(
        isApiError(err)
          ? (err.error?.message ?? t("metricCreateErrorToast"))
          : t("metricCreateErrorToast"),
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
        <FieldLabel htmlFor="metric-slug">{t("slugLabel")}</FieldLabel>
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
        <FieldLabel htmlFor="metric-name-en">{t("nameEnLabel")}</FieldLabel>
        <input
          id="metric-name-en"
          className={inputClass}
          data-testid="author-metric-name-en-input"
          {...register("nameEn")}
        />
        <FieldError>{errors.nameEn?.message}</FieldError>
      </Field>
      <Field>
        <FieldLabel htmlFor="metric-name-ru">{t("nameRuLabel")}</FieldLabel>
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
        {t("create")}
      </Button>
    </form>
  );
}

function MetricValuesEditor({ metric }: { metric: MyAuthorMetricDefinition }) {
  const t = useTranslations("authorMetricsStudio");
  const locale = useAppLocale();
  const countries = useQuery(allCountriesQuery(toApiLocale(locale)));
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
      toast.success(t("valuesSavedToast"));
    } catch (err: unknown) {
      toast.error(
        isApiError(err)
          ? (err.error?.message ?? t("valuesSaveErrorToast"))
          : t("valuesSaveErrorToast"),
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
        {t("saveValues")}
      </Button>
    </div>
  );
}

function MetricRow({ metric }: { metric: MyAuthorMetricDefinition }) {
  const t = useTranslations("authorMetricsStudio");
  const locale = useAppLocale();
  const apiLocale = toApiLocale(locale);
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
              {apiLocale === "ru" ? metric.name_ru : metric.name_en}
            </span>
            <span className="text-c4 font-mono text-xs">{metric.slug}</span>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="default">
              {moderationStatusLabel(metric.status, locale)}
            </Badge>
            <Button
              variant="ghost"
              onClick={() => setExpanded((current) => !current)}
            >
              {expanded ? t("hideValues") : t("valuesByCountry")}
            </Button>
            <Button
              variant="ghost"
              onClick={() => submitMetric.mutate(metric.id)}
              disabled={metric.status !== "draft" || submitMetric.isPending}
              data-testid="author-metric-submit"
            >
              {t("submitToModeration")}
            </Button>
            <Button
              variant="ghost"
              onClick={() => archiveMetric.mutate(metric.id)}
              disabled={metric.status === "archived" || archiveMetric.isPending}
            >
              {t("archive")}
            </Button>
          </div>
        </div>
        {expanded && <MetricValuesEditor metric={metric} />}
      </Card>
    </div>
  );
}

export function AuthorMetricsStudioView() {
  const t = useTranslations("authorMetricsStudio");
  const { user, isLoading: authLoading } = useAuth();
  const metrics = useQuery({
    ...myAuthorMetricsQuery(),
    enabled: Boolean(user),
  });

  if (authLoading) {
    return <LoadingState message={t("loading")} />;
  }

  if (!user) {
    return (
      <div
        className="border-warm flex flex-col gap-2 border px-4 py-4"
        data-testid="author-metrics-unauthenticated"
      >
        <p className="text-c3 text-sm">
          {t("loginRequired")}{" "}
          <Link
            href={routes.login}
            className="text-c1 hover:text-gold3 underline decoration-dotted underline-offset-2 transition-colors duration-200"
          >
            {t("loginLabel")}
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
        <Kicker>{t("newMetricKicker")}</Kicker>
        <CreateMetricForm />
      </Card>

      <div className="flex flex-col gap-4">
        <Kicker>{t("myMetricsKicker")}</Kicker>
        {metrics.isPending ? (
          <LoadingState message={t("loadingMetrics")} />
        ) : metrics.isError ? (
          <ErrorState
            error={isApiError(metrics.error) ? metrics.error : undefined}
          />
        ) : (metrics.data.items ?? []).length === 0 ? (
          <div data-testid="author-metrics-empty-state">
            <EmptyState message={t("emptyMetrics")} />
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
