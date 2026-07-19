"use client";

import { useQuery } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
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
import { useAppLocale } from "../../shared/lib/useAppLocale";
import { routes } from "../../shared/lib/routes";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";
import { migrationBoardErrorMessage } from "./errorMessage";

export function AccountMigrationBoardView() {
  const t = useTranslations("migrationBoardAccount");
  const { user, isLoading: authLoading } = useAuth();
  const locale = useAppLocale();

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
    return <LoadingState message={t("loadingBoard")} />;
  }

  if (!user) {
    return (
      <ErrorState
        error={t("loginRequired")}
        backHref={getPathname({ href: routes.login, locale })}
        backLabel={t("loginLabel")}
      />
    );
  }

  if (posts.isPending || incoming.isPending || outgoing.isPending) {
    return <LoadingState message={t("loadingBoard")} />;
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
        <ErrorState error={migrationBoardErrorMessage(loadError, locale)} />
      )}
      <div className="flex flex-wrap gap-3">
        <Link href={routes.migrationBoardNew}>
          <Button>{t("createPost")}</Button>
        </Link>
        <Link href={routes.migrationBoard}>
          <Button variant="ghost">{t("publicBoard")}</Button>
        </Link>
      </div>

      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <Kicker>{t("myPostsKicker")}</Kicker>
        {postItems.length === 0 ? (
          <EmptyState message={t("emptyPosts")} />
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
                    {t("submitToModeration")}
                  </Button>
                  <Button
                    variant="ghost"
                    onClick={() => archivePost.mutate(post.id)}
                    disabled={
                      post.status === "archived" || archivePost.isPending
                    }
                  >
                    {t("archive")}
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
        <Kicker>{t("incomingKicker")}</Kicker>
        {incomingItems.length === 0 ? (
          <p className="text-c3 text-sm">{t("noIncoming")}</p>
        ) : (
          incomingItems.map((request) => (
            <div
              key={request.id}
              className="border-warm flex items-center justify-between gap-4 border-b py-3 last:border-b-0"
            >
              <span className="text-c2 text-sm">
                {t("fromRequestLine", {
                  post: request.post_title,
                  name: request.from_user_display_name,
                  status: request.status,
                })}
              </span>
              <div className="flex gap-3">
                <Button
                  variant="ghost"
                  onClick={() => acceptRequest.mutate(request.id)}
                  disabled={acceptRequest.isPending}
                >
                  {t("accept")}
                </Button>
                <Button
                  variant="ghost"
                  onClick={() => declineRequest.mutate(request.id)}
                  disabled={declineRequest.isPending}
                >
                  {t("decline")}
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
        <Kicker>{t("outgoingKicker")}</Kicker>
        {outgoingItems.length === 0 ? (
          <p className="text-c3 text-sm">{t("noOutgoing")}</p>
        ) : (
          outgoingItems.map((request) => (
            <div
              key={request.id}
              className="border-warm flex items-center justify-between gap-4 border-b py-3 last:border-b-0"
            >
              <span className="text-c2 text-sm">
                {t("toRequestLine", {
                  post: request.post_title,
                  name: request.to_user_display_name,
                  status: request.status,
                })}
              </span>
              <Button
                variant="ghost"
                onClick={() => cancelRequest.mutate(request.id)}
                disabled={
                  request.status !== "pending" || cancelRequest.isPending
                }
              >
                {t("cancel")}
              </Button>
            </div>
          ))
        )}
      </Card>
    </div>
  );
}
