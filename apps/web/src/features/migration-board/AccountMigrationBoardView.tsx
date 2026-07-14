"use client";

import { useQuery } from "@tanstack/react-query";
import { useLocale } from "next-intl";
import { Badge, Button, Card, Kicker } from "@country-decision-atlas/ui";
import { Link, getPathname } from "../../i18n/navigation";
import {
  myBoardPostsQuery,
  incomingContactRequestsQuery,
  outgoingContactRequestsQuery,
  useAcceptContactRequestMutation,
  useArchiveBoardPostMutation,
  useCancelContactRequestMutation,
  useDeclineContactRequestMutation,
  useSubmitBoardPostMutation,
} from "../../entities/migration-board/api";
import { useAuth } from "../../shared/auth/AuthProvider";
import { routes } from "../../shared/lib/routes";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";
import { migrationBoardErrorMessage } from "./errorMessage";

export function AccountMigrationBoardView() {
  const { user, isLoading: authLoading } = useAuth();
  const locale = useLocale();

  const posts = useQuery({ ...myBoardPostsQuery(), enabled: Boolean(user) });
  const incoming = useQuery({
    ...incomingContactRequestsQuery(),
    enabled: Boolean(user),
  });
  const outgoing = useQuery({
    ...outgoingContactRequestsQuery(),
    enabled: Boolean(user),
  });

  const submitPost = useSubmitBoardPostMutation();
  const archivePost = useArchiveBoardPostMutation();
  const acceptRequest = useAcceptContactRequestMutation();
  const declineRequest = useDeclineContactRequestMutation();
  const cancelRequest = useCancelContactRequestMutation();

  if (authLoading) {
    return <LoadingState message="Загрузка migration board…" />;
  }

  if (!user) {
    return (
      <ErrorState
        error="Войдите, чтобы видеть свои записи."
        backHref={getPathname({ href: routes.login, locale })}
        backLabel="Войти"
      />
    );
  }

  if (posts.isPending || incoming.isPending || outgoing.isPending) {
    return <LoadingState message="Загрузка migration board…" />;
  }

  const loadError = posts.error ?? incoming.error ?? outgoing.error;
  const postItems = posts.data?.items ?? [];
  const incomingItems = incoming.data?.items ?? [];
  const outgoingItems = outgoing.data?.items ?? [];

  return (
    <div
      className="flex flex-col gap-8"
      data-testid="account-migration-board"
    >
      {loadError != null && (
        <ErrorState error={migrationBoardErrorMessage(loadError)} />
      )}
      <div className="flex flex-wrap gap-3">
        <Link href={routes.migrationBoardNew}>
          <Button>Создать запись</Button>
        </Link>
        <Link href={routes.migrationBoard}>
          <Button variant="ghost">Публичная доска</Button>
        </Link>
      </div>

      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <Kicker>Мои записи</Kicker>
        {postItems.length === 0 ? (
          <EmptyState message="Записей пока нет." />
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {postItems.map((post) => (
              <Card
                key={post.id}
                interactive={false}
                className="flex flex-col gap-3"
              >
                <span className="text-c4 text-xs">
                  {post.destination_country.name}
                </span>
                <span className="font-display text-lg font-semibold">
                  {post.title}
                </span>
                <p className="text-c3 text-sm">{post.summary}</p>
                <div className="flex flex-wrap gap-2">
                  <Badge variant="default">{post.status}</Badge>
                  <Badge variant="default">{post.moderation_status}</Badge>
                </div>
                <div className="flex gap-3">
                  <Button
                    variant="ghost"
                    onClick={() => submitPost.mutate(post.id)}
                    disabled={
                      post.status === "review" ||
                      post.status === "published" ||
                      submitPost.isPending
                    }
                    data-testid="migration-board-account-submit"
                  >
                    На модерацию
                  </Button>
                  <Button
                    variant="ghost"
                    onClick={() => archivePost.mutate(post.id)}
                    disabled={
                      post.status === "archived" || archivePost.isPending
                    }
                  >
                    Архив
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}
      </Card>

      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <Kicker>Входящие requests</Kicker>
        {incomingItems.length === 0 ? (
          <p className="text-c3 text-sm">Нет входящих requests.</p>
        ) : (
          incomingItems.map((request) => (
            <div
              key={request.id}
              className="border-warm flex items-center justify-between gap-4 border-b py-3 last:border-b-0"
            >
              <span className="text-c2 text-sm">
                {request.post_title} от {request.from_user_display_name}:{" "}
                {request.status}
              </span>
              <div className="flex gap-3">
                <Button
                  variant="ghost"
                  onClick={() => acceptRequest.mutate(request.id)}
                  disabled={acceptRequest.isPending}
                >
                  Accept
                </Button>
                <Button
                  variant="ghost"
                  onClick={() => declineRequest.mutate(request.id)}
                  disabled={declineRequest.isPending}
                >
                  Decline
                </Button>
              </div>
            </div>
          ))
        )}
      </Card>

      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <Kicker>Исходящие requests</Kicker>
        {outgoingItems.length === 0 ? (
          <p className="text-c3 text-sm">Нет исходящих requests.</p>
        ) : (
          outgoingItems.map((request) => (
            <div
              key={request.id}
              className="border-warm flex items-center justify-between gap-4 border-b py-3 last:border-b-0"
            >
              <span className="text-c2 text-sm">
                {request.post_title} для {request.to_user_display_name}:{" "}
                {request.status}
              </span>
              <Button
                variant="ghost"
                onClick={() => cancelRequest.mutate(request.id)}
                disabled={
                  request.status !== "pending" || cancelRequest.isPending
                }
              >
                Cancel
              </Button>
            </div>
          ))
        )}
      </Card>
    </div>
  );
}
