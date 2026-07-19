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
  FieldHint,
  FieldLabel,
  Kicker,
  toast,
} from "@country-decision-atlas/ui";
import { allCountriesQuery, scenariosQuery } from "../../entities/decision/api";
import {
  useCreateUserStoryMutation,
  userStoriesQuery,
} from "../../entities/user-stories/api";
import type { UserStory } from "../../shared/api/user-stories";
import { isApiError } from "../../shared/api/http";
import { useAppLocale } from "../../shared/lib/useAppLocale";
import { toApiLocale } from "../../shared/lib/locale";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";

const inputClass =
  "border-warm bg-bg2 text-c1 font-body border px-4 py-2.5 text-sm outline-none focus-visible:border-gold transition-colors duration-200";
const textareaClass = inputClass;
const selectClass =
  "border-warm bg-bg2 text-c2 focus-visible:border-gold w-full border px-3 py-2 text-sm outline-none";

function StoryCard({
  story,
  countryName,
}: {
  story: UserStory;
  countryName: string;
}) {
  const t = useTranslations("userStories");
  const excerpt =
    story.positive_outcome || story.advice || story.problems || story.notes;

  return (
    <div data-testid="user-story-card">
      <Card
        interactive={false}
        className="flex flex-col gap-3"
      >
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="default">{countryName}</Badge>
          <Badge variant="default">{story.scenario}</Badge>
          {story.is_synthetic && (
            <span data-testid="user-story-synthetic-badge">
              <Badge variant="warning">synthetic</Badge>
            </span>
          )}
          {story.year && <Badge variant="default">{story.year}</Badge>}
        </div>
        {excerpt && (
          <p className="font-quote text-c2 text-base italic leading-relaxed">
            “{excerpt}”
          </p>
        )}
        {story.advice && story.advice !== excerpt && (
          <p className="text-c3 text-sm">
            <span className="text-c4">{t("adviceLabel")}</span> {story.advice}
          </p>
        )}
        {story.satisfaction_score && (
          <p className="text-c4 text-xs">
            {t("satisfactionLabel", { score: story.satisfaction_score })}
          </p>
        )}
      </Card>
    </div>
  );
}

function SubmitStoryForm() {
  const t = useTranslations("userStories");
  const locale = useAppLocale();
  const apiLocale = toApiLocale(locale);
  const countries = useQuery(allCountriesQuery(apiLocale));
  const scenarios = useQuery(scenariosQuery(apiLocale));
  const createStory = useCreateUserStoryMutation();

  const submitStorySchema = z.object({
    destinationCountrySlug: z.string().min(1, t("chooseCountryError")),
    scenario: z.string().min(1, t("chooseScenarioError")),
    positiveOutcome: z.string().optional(),
    advice: z.string().optional(),
  });
  type SubmitStoryValues = z.infer<typeof submitStorySchema>;

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<SubmitStoryValues>({ resolver: zodResolver(submitStorySchema) });

  async function onSubmit(values: SubmitStoryValues) {
    try {
      await createStory.mutateAsync({
        destination_country_slug: values.destinationCountrySlug,
        scenario: values.scenario,
        positive_outcome: values.positiveOutcome || null,
        advice: values.advice || null,
        is_synthetic: true,
        notes: "Synthetic example submitted via the community stories form.",
      });
      reset();
      toast.success(t("storySavedToast"));
    } catch (err: unknown) {
      toast.error(
        isApiError(err)
          ? (err.error?.message ?? t("storyErrorToast"))
          : t("storyErrorToast"),
      );
    }
  }

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="flex flex-col gap-4"
      noValidate
    >
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Field>
          <FieldLabel htmlFor="story-destination">
            {t("destinationCountryLabel")}
          </FieldLabel>
          <select
            id="story-destination"
            className={selectClass}
            data-testid="user-story-destination-select"
            {...register("destinationCountrySlug")}
          >
            <option value="">{t("chooseCountryOption")}</option>
            {countries.data?.items.map((c) => (
              <option
                key={c.slug}
                value={c.slug}
              >
                {c.name}
              </option>
            ))}
          </select>
          <FieldError>{errors.destinationCountrySlug?.message}</FieldError>
        </Field>
        <Field>
          <FieldLabel htmlFor="story-scenario">{t("scenarioLabel")}</FieldLabel>
          <select
            id="story-scenario"
            className={selectClass}
            data-testid="user-story-scenario-input"
            {...register("scenario")}
          >
            <option value="">{t("chooseScenarioOption")}</option>
            {scenarios.data?.items.map((s) => (
              <option
                key={s.slug}
                value={s.slug}
              >
                {s.name}
              </option>
            ))}
          </select>
          <FieldError>{errors.scenario?.message}</FieldError>
        </Field>
      </div>
      <Field>
        <FieldLabel htmlFor="story-positive">
          {t("positiveOutcomeLabel")}
        </FieldLabel>
        <textarea
          id="story-positive"
          className={textareaClass}
          rows={3}
          data-testid="user-story-positive-input"
          {...register("positiveOutcome")}
        />
      </Field>
      <Field>
        <FieldLabel htmlFor="story-advice">{t("adviceFieldLabel")}</FieldLabel>
        <textarea
          id="story-advice"
          className={textareaClass}
          rows={3}
          data-testid="user-story-advice-input"
          {...register("advice")}
        />
        <FieldHint>{t("privacyNotice")}</FieldHint>
      </Field>
      <Button
        type="submit"
        disabled={createStory.isPending}
        data-testid="user-story-submit"
      >
        {createStory.isPending ? t("submitting") : t("submitStory")}
      </Button>
    </form>
  );
}

export function UserStoriesView() {
  const t = useTranslations("userStories");
  const locale = useAppLocale();
  const countries = useQuery(allCountriesQuery(toApiLocale(locale)));
  const stories = useQuery(userStoriesQuery());

  const countryNameById = new Map(
    countries.data?.items.map((c) => [c.id, c.name]) ?? [],
  );

  return (
    <div
      className="flex flex-col gap-8"
      data-testid="user-stories-view"
    >
      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <Kicker>{t("shareStoryKicker")}</Kicker>
        <SubmitStoryForm />
      </Card>

      <div className="flex flex-col gap-4">
        <Kicker>{t("communityStoriesKicker")}</Kicker>
        {stories.isPending ? (
          <LoadingState message={t("loadingStories")} />
        ) : stories.isError ? (
          <ErrorState
            error={isApiError(stories.error) ? stories.error : undefined}
          />
        ) : (stories.data.items ?? []).length === 0 ? (
          <div data-testid="user-stories-empty-state">
            <EmptyState message={t("emptyStories")} />
          </div>
        ) : (
          <div
            className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
            data-testid="user-stories-list"
          >
            {(stories.data.items ?? []).map((story) => (
              <StoryCard
                key={story.id}
                story={story}
                countryName={
                  countryNameById.get(story.destination_country_id) ??
                  t("unknownCountry")
                }
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
