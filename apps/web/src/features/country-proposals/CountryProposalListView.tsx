"use client";

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
import { Link } from "../../i18n/navigation";
import {
  myCountryProposalsQuery,
  useCreateCountryProposalMutation,
} from "../../entities/country-proposals/api";
import { isApiError } from "../../shared/api/http";
import { useAuth } from "../../shared/auth/AuthProvider";
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

const createProposalSchema = z.object({
  slug: z
    .string()
    .min(1, "Введите slug")
    .regex(
      /^[a-z0-9_-]+$/,
      "Только строчные буквы, цифры, дефис и подчёркивание",
    ),
  nameEn: z.string().min(1, "Введите название (en)"),
  nameRu: z.string().min(1, "Введите название (ru)"),
  iso2: z.string().length(2, "ISO2 — ровно 2 символа"),
  iso3: z.string().length(3, "ISO3 — ровно 3 символа"),
  justification: z.string().min(1, "Опишите обоснование"),
});
type CreateProposalValues = z.infer<typeof createProposalSchema>;

function CreateProposalForm() {
  const createProposal = useCreateCountryProposalMutation();
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<CreateProposalValues>({
    resolver: zodResolver(createProposalSchema),
  });

  async function onSubmit(values: CreateProposalValues) {
    try {
      await createProposal.mutateAsync({
        slug: values.slug,
        name_en: values.nameEn,
        name_ru: values.nameRu,
        iso2: values.iso2.toUpperCase(),
        iso3: values.iso3.toUpperCase(),
        justification: values.justification,
      });
      reset();
      toast.success("Заявка страны создана как черновик.");
    } catch (err: unknown) {
      toast.error(
        isApiError(err)
          ? (err.error?.message ?? "Не удалось создать заявку.")
          : "Не удалось создать заявку.",
      );
    }
  }

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="flex flex-col gap-4"
      noValidate
    >
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Field>
          <FieldLabel htmlFor="proposal-slug">Slug</FieldLabel>
          <input
            id="proposal-slug"
            className={inputClass}
            placeholder="paraguay"
            data-testid="country-proposal-slug-input"
            {...register("slug")}
          />
          <FieldError>{errors.slug?.message}</FieldError>
        </Field>
        <Field>
          <FieldLabel htmlFor="proposal-name-en">Название (en)</FieldLabel>
          <input
            id="proposal-name-en"
            className={inputClass}
            data-testid="country-proposal-name-en-input"
            {...register("nameEn")}
          />
          <FieldError>{errors.nameEn?.message}</FieldError>
        </Field>
        <Field>
          <FieldLabel htmlFor="proposal-name-ru">Название (ru)</FieldLabel>
          <input
            id="proposal-name-ru"
            className={inputClass}
            data-testid="country-proposal-name-ru-input"
            {...register("nameRu")}
          />
          <FieldError>{errors.nameRu?.message}</FieldError>
        </Field>
        <div className="grid grid-cols-2 gap-2">
          <Field>
            <FieldLabel htmlFor="proposal-iso2">ISO2</FieldLabel>
            <input
              id="proposal-iso2"
              className={inputClass}
              maxLength={2}
              data-testid="country-proposal-iso2-input"
              {...register("iso2")}
            />
            <FieldError>{errors.iso2?.message}</FieldError>
          </Field>
          <Field>
            <FieldLabel htmlFor="proposal-iso3">ISO3</FieldLabel>
            <input
              id="proposal-iso3"
              className={inputClass}
              maxLength={3}
              data-testid="country-proposal-iso3-input"
              {...register("iso3")}
            />
            <FieldError>{errors.iso3?.message}</FieldError>
          </Field>
        </div>
      </div>
      <Field>
        <FieldLabel htmlFor="proposal-justification">Обоснование</FieldLabel>
        <textarea
          id="proposal-justification"
          className={inputClass}
          rows={3}
          data-testid="country-proposal-justification-input"
          {...register("justification")}
        />
        <FieldError>{errors.justification?.message}</FieldError>
      </Field>
      <Button
        type="submit"
        disabled={createProposal.isPending}
        data-testid="country-proposal-create-submit"
      >
        Создать заявку
      </Button>
    </form>
  );
}

export function CountryProposalListView() {
  const { user, isLoading: authLoading } = useAuth();
  const proposals = useQuery({
    ...myCountryProposalsQuery(),
    enabled: Boolean(user),
  });

  if (authLoading) {
    return <LoadingState message="Загрузка…" />;
  }

  if (!user) {
    return (
      <div
        className="border-warm flex flex-col gap-2 border px-4 py-4"
        data-testid="country-proposals-unauthenticated"
      >
        <p className="text-c3 text-sm">
          Войдите, чтобы предложить страну.{" "}
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
      data-testid="country-proposals-list-view"
    >
      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <Kicker>Новая заявка</Kicker>
        <CreateProposalForm />
      </Card>

      <div className="flex flex-col gap-4">
        <Kicker>Мои заявки</Kicker>
        {proposals.isPending ? (
          <LoadingState message="Загрузка заявок…" />
        ) : proposals.isError ? (
          <ErrorState
            error={isApiError(proposals.error) ? proposals.error : undefined}
          />
        ) : (proposals.data.items ?? []).length === 0 ? (
          <div data-testid="country-proposals-empty-state">
            <EmptyState message="Заявок пока нет." />
          </div>
        ) : (
          <div
            className="grid grid-cols-1 gap-4 sm:grid-cols-2"
            data-testid="country-proposals-list"
          >
            {(proposals.data.items ?? []).map((proposal) => (
              <Link
                key={proposal.id}
                href={routes.countryProposalWizard(proposal.id)}
                data-testid="country-proposal-item"
              >
                <Card className="flex h-full flex-col gap-3">
                  <span className="font-display text-lg font-semibold">
                    {proposal.name_ru}
                  </span>
                  <span className="text-c4 font-mono text-xs">
                    {proposal.slug}
                  </span>
                  <Badge variant="default">
                    {STATUS_LABELS[proposal.status] ?? proposal.status}
                  </Badge>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
