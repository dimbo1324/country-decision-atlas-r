"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useQuery } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { z } from "zod";
import {
  Badge,
  BoardGrid,
  Button,
  Card,
  Field,
  FieldError,
  FieldHint,
  FieldLabel,
  Kicker,
  TimelineList,
  type TimelineEvent,
  toast,
} from "@country-decision-atlas/ui";
import { Link } from "../../i18n/navigation";
import {
  subscriptionsFeedQuery,
  subscriptionsQuery,
  useCreateSubscriptionMutation,
  useDeleteSubscriptionMutation,
} from "../../entities/subscriptions/api";
import type { FeedEntryResponse } from "../../shared/api/subscriptions";
import { isApiError } from "../../shared/api/http";
import { useAuth } from "../../shared/auth/AuthProvider";
import { routes } from "../../shared/lib/routes";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";
import { formatDate } from "../../shared/lib/format";

const inputClass =
  "border-warm bg-bg2 text-c1 font-body border px-4 py-2.5 text-sm outline-none focus-visible:border-gold transition-colors duration-200";

const subscribeSchema = z
  .object({
    metricId: z.string().optional(),
    authorUserId: z.string().optional(),
  })
  .refine((v) => Boolean(v.metricId) || Boolean(v.authorUserId), {
    message: "Укажите ID метрики или ID автора.",
    path: ["metricId"],
  });
type SubscribeValues = z.infer<typeof subscribeSchema>;

function SubscribeForm() {
  const createSubscription = useCreateSubscriptionMutation();
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<SubscribeValues>({ resolver: zodResolver(subscribeSchema) });

  async function onSubmit(values: SubscribeValues) {
    try {
      await createSubscription.mutateAsync({
        metric_id: values.metricId || null,
        author_user_id: values.authorUserId || null,
      });
      reset();
      toast.success("Подписка добавлена.");
    } catch (err: unknown) {
      toast.error(
        isApiError(err)
          ? (err.error?.message ?? "Не удалось оформить подписку.")
          : "Не удалось оформить подписку.",
      );
    }
  }

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="flex flex-col gap-4 sm:flex-row sm:items-end"
      noValidate
    >
      <Field className="flex-1">
        <FieldLabel htmlFor="subscribe-metric-id">ID метрики</FieldLabel>
        <input
          id="subscribe-metric-id"
          type="text"
          className={inputClass}
          data-testid="subscribe-metric-id-input"
          {...register("metricId")}
        />
        <FieldError>{errors.metricId?.message}</FieldError>
      </Field>
      <Field className="flex-1">
        <FieldLabel htmlFor="subscribe-author-id">
          Или ID автора (все его метрики)
        </FieldLabel>
        <input
          id="subscribe-author-id"
          type="text"
          className={inputClass}
          data-testid="subscribe-author-id-input"
          {...register("authorUserId")}
        />
        <FieldHint>Заполните одно из двух полей.</FieldHint>
      </Field>
      <Button
        type="submit"
        disabled={createSubscription.isPending}
        data-testid="subscribe-submit"
      >
        {createSubscription.isPending ? "Подписываем…" : "Подписаться"}
      </Button>
    </form>
  );
}

function feedEntryToTimelineEvent(entry: FeedEntryResponse): TimelineEvent {
  return {
    id: `${entry.metric_id}-${entry.value_updated_at}`,
    date: formatDate(entry.value_updated_at),
    impact: "info",
    impactLabel: `${entry.country_name} · ${entry.value}`,
    title: entry.metric_name_ru,
    source: entry.author.display_name,
  };
}

export function SubscriptionsView() {
  const { user, isLoading: isAuthLoading } = useAuth();
  const subscriptions = useQuery({
    ...subscriptionsQuery(),
    enabled: Boolean(user),
  });
  const feed = useQuery({
    ...subscriptionsFeedQuery(),
    enabled: Boolean(user),
  });
  const deleteSubscription = useDeleteSubscriptionMutation();

  if (isAuthLoading) {
    return <LoadingState message="Загрузка…" />;
  }

  if (!user) {
    return (
      <div
        className="border-warm flex flex-col gap-2 border px-4 py-4"
        data-testid="subscriptions-unauthenticated"
      >
        <p className="text-c3 text-sm">
          Войдите, чтобы управлять подписками.{" "}
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

  if (subscriptions.isPending || feed.isPending) {
    return <LoadingState message="Загрузка подписок…" />;
  }

  const loadError = subscriptions.error ?? feed.error;
  if (loadError) {
    return (
      <div data-testid="subscriptions-error">
        <ErrorState error={isApiError(loadError) ? loadError : undefined} />
      </div>
    );
  }

  const subscriptionItems = subscriptions.data?.items ?? [];
  const feedItems = feed.data?.items ?? [];

  return (
    <div
      className="flex flex-col gap-8"
      data-testid="subscriptions-view"
    >
      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <Kicker>Новая подписка</Kicker>
        <SubscribeForm />
      </Card>

      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <Kicker>Мои подписки</Kicker>
        {subscriptionItems.length === 0 ? (
          <p
            className="text-c3 text-sm"
            data-testid="subscriptions-empty-state"
          >
            Вы пока ни на что не подписаны.
          </p>
        ) : (
          <BoardGrid data-testid="subscriptions-list">
            {subscriptionItems.map((subscription) => (
              <div
                key={subscription.id}
                data-testid="subscription-item"
              >
                <Card
                  interactive={false}
                  className="flex h-full flex-col gap-3"
                >
                  <span className="font-display text-lg font-semibold">
                    {subscription.metric_name_en ??
                      (subscription.author_display_name
                        ? `Автор: ${subscription.author_display_name}`
                        : "Подписка")}
                  </span>
                  {subscription.metric_slug && (
                    <Badge variant="default">{subscription.metric_slug}</Badge>
                  )}
                  <Button
                    variant="ghost"
                    onClick={() => deleteSubscription.mutate(subscription.id)}
                    data-testid="subscription-remove-button"
                    className="self-start"
                  >
                    Отписаться
                  </Button>
                </Card>
              </div>
            ))}
          </BoardGrid>
        )}
      </Card>

      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <Kicker>Лента</Kicker>
        {feedItems.length === 0 ? (
          <div data-testid="feed-empty-state">
            <EmptyState message="Пока нет обновлений по вашим подпискам." />
          </div>
        ) : (
          <div data-testid="feed-list">
            <TimelineList events={feedItems.map(feedEntryToTimelineEvent)} />
          </div>
        )}
      </Card>
    </div>
  );
}
