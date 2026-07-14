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
            <span className="text-c4">Совет:</span> {story.advice}
          </p>
        )}
        {story.satisfaction_score && (
          <p className="text-c4 text-xs">
            Удовлетворённость: {story.satisfaction_score}/10
          </p>
        )}
      </Card>
    </div>
  );
}

const submitStorySchema = z.object({
  destinationCountrySlug: z.string().min(1, "Выберите страну"),
  scenario: z.string().min(1, "Укажите сценарий"),
  positiveOutcome: z.string().optional(),
  advice: z.string().optional(),
});
type SubmitStoryValues = z.infer<typeof submitStorySchema>;

function SubmitStoryForm() {
  const locale = useAppLocale();
  const countries = useQuery(allCountriesQuery(locale));
  const scenarios = useQuery(scenariosQuery(locale));
  const createStory = useCreateUserStoryMutation();
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
      toast.success(
        "История сохранена и будет опубликована после проверки модератором.",
      );
    } catch (err: unknown) {
      toast.error(
        isApiError(err)
          ? (err.error?.message ?? "Не удалось отправить историю.")
          : "Не удалось отправить историю.",
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
          <FieldLabel htmlFor="story-destination">Страна назначения</FieldLabel>
          <select
            id="story-destination"
            className={selectClass}
            data-testid="user-story-destination-select"
            {...register("destinationCountrySlug")}
          >
            <option value="">Выберите страну</option>
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
          <FieldLabel htmlFor="story-scenario">Сценарий</FieldLabel>
          <select
            id="story-scenario"
            className={selectClass}
            data-testid="user-story-scenario-input"
            {...register("scenario")}
          >
            <option value="">Выберите сценарий</option>
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
        <FieldLabel htmlFor="story-positive">Что получилось хорошо</FieldLabel>
        <textarea
          id="story-positive"
          className={textareaClass}
          rows={3}
          data-testid="user-story-positive-input"
          {...register("positiveOutcome")}
        />
      </Field>
      <Field>
        <FieldLabel htmlFor="story-advice">Совет другим</FieldLabel>
        <textarea
          id="story-advice"
          className={textareaClass}
          rows={3}
          data-testid="user-story-advice-input"
          {...register("advice")}
        />
        <FieldHint>
          Не публикуйте контакты (email, телефон, Telegram) в открытом тексте.
        </FieldHint>
      </Field>
      <Button
        type="submit"
        disabled={createStory.isPending}
        data-testid="user-story-submit"
      >
        {createStory.isPending ? "Отправляем…" : "Отправить историю"}
      </Button>
    </form>
  );
}

export function UserStoriesView() {
  const locale = useAppLocale();
  const countries = useQuery(allCountriesQuery(locale));
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
        <Kicker>Поделиться историей</Kicker>
        <SubmitStoryForm />
      </Card>

      <div className="flex flex-col gap-4">
        <Kicker>Истории сообщества</Kicker>
        {stories.isPending ? (
          <LoadingState message="Загрузка историй…" />
        ) : stories.isError ? (
          <ErrorState
            error={isApiError(stories.error) ? stories.error : undefined}
          />
        ) : (stories.data.items ?? []).length === 0 ? (
          <div data-testid="user-stories-empty-state">
            <EmptyState message="Историй пока нет." />
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
                  "Неизвестная страна"
                }
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
