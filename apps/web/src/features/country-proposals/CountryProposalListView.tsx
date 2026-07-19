"use client";

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
import { Link } from "../../i18n/navigation";
import {
  myCountryProposalsQuery,
  useCreateCountryProposalMutation,
} from "../../entities/country-proposals/api";
import { isApiError } from "../../shared/api/http";
import { useAuth } from "../../shared/auth/AuthProvider";
import { useAppLocale } from "../../shared/lib/useAppLocale";
import { toApiLocale } from "../../shared/lib/locale";
import { moderationStatusLabel } from "../../shared/lib/moderation-status-labels";
import { routes } from "../../shared/lib/routes";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";

const inputClass =
  "border-warm bg-bg2 text-c1 font-body border px-4 py-2.5 text-sm outline-none focus-visible:border-gold transition-colors duration-200";

function CreateProposalForm() {
  const t = useTranslations("countryProposals");
  const createProposal = useCreateCountryProposalMutation();

  const createProposalSchema = z.object({
    slug: z
      .string()
      .min(1, t("slugRequired"))
      .regex(/^[a-z0-9_-]+$/, t("slugPattern")),
    nameEn: z.string().min(1, t("nameEnRequired")),
    nameRu: z.string().min(1, t("nameRuRequired")),
    iso2: z.string().length(2, t("iso2Length")),
    iso3: z.string().length(3, t("iso3Length")),
    justification: z.string().min(1, t("justificationRequired")),
  });
  type CreateProposalValues = z.infer<typeof createProposalSchema>;

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
      toast.success(t("proposalCreatedToast"));
    } catch (err: unknown) {
      toast.error(
        isApiError(err)
          ? (err.error?.message ?? t("proposalCreateErrorToast"))
          : t("proposalCreateErrorToast"),
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
          <FieldLabel htmlFor="proposal-slug">{t("slugLabel")}</FieldLabel>
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
          <FieldLabel htmlFor="proposal-name-en">{t("nameEnLabel")}</FieldLabel>
          <input
            id="proposal-name-en"
            className={inputClass}
            data-testid="country-proposal-name-en-input"
            {...register("nameEn")}
          />
          <FieldError>{errors.nameEn?.message}</FieldError>
        </Field>
        <Field>
          <FieldLabel htmlFor="proposal-name-ru">{t("nameRuLabel")}</FieldLabel>
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
        <FieldLabel htmlFor="proposal-justification">
          {t("justificationLabel")}
        </FieldLabel>
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
        {t("createProposal")}
      </Button>
    </form>
  );
}

export function CountryProposalListView() {
  const t = useTranslations("countryProposals");
  const locale = useAppLocale();
  const apiLocale = toApiLocale(locale);
  const { user, isLoading: authLoading } = useAuth();
  const proposals = useQuery({
    ...myCountryProposalsQuery(),
    enabled: Boolean(user),
  });

  if (authLoading) {
    return <LoadingState message={t("loading")} />;
  }

  if (!user) {
    return (
      <div
        className="border-warm flex flex-col gap-2 border px-4 py-4"
        data-testid="country-proposals-unauthenticated"
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
      data-testid="country-proposals-list-view"
    >
      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <Kicker>{t("newProposalKicker")}</Kicker>
        <CreateProposalForm />
      </Card>

      <div className="flex flex-col gap-4">
        <Kicker>{t("myProposalsKicker")}</Kicker>
        {proposals.isPending ? (
          <LoadingState message={t("loadingProposals")} />
        ) : proposals.isError ? (
          <ErrorState
            error={isApiError(proposals.error) ? proposals.error : undefined}
          />
        ) : (proposals.data.items ?? []).length === 0 ? (
          <div data-testid="country-proposals-empty-state">
            <EmptyState message={t("emptyProposals")} />
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
                    {apiLocale === "ru" ? proposal.name_ru : proposal.name_en}
                  </span>
                  <span className="text-c4 font-mono text-xs">
                    {proposal.slug}
                  </span>
                  <Badge variant="default">
                    {moderationStatusLabel(proposal.status, locale)}
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
