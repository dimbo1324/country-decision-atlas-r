"use client";

import { useQuery } from "@tanstack/react-query";
import { Button, Card, Kicker } from "@country-decision-atlas/ui";
import {
  adminBoardPostsQuery,
  adminBoardReportsQuery,
  useApproveAdminBoardPostMutation,
  useDismissAdminBoardReportMutation,
  useHideAdminBoardPostMutation,
  useRejectAdminBoardPostMutation,
  useResolveAdminBoardReportMutation,
} from "../../entities/migration-board/api";
import { MODERATION_ROLES } from "../../shared/auth/roles";
import { useAuthGuard } from "../../shared/auth/useAuthGuard";
import { routes } from "../../shared/lib/routes";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";
import { migrationBoardErrorMessage } from "./errorMessage";

export function MigrationBoardModerationView() {
  const { status } = useAuthGuard(MODERATION_ROLES);

  const posts = useQuery({
    ...adminBoardPostsQuery("review"),
    enabled: status === "ok",
  });
  const reports = useQuery({
    ...adminBoardReportsQuery(),
    enabled: status === "ok",
  });

  const approvePost = useApproveAdminBoardPostMutation();
  const rejectPost = useRejectAdminBoardPostMutation();
  const hidePost = useHideAdminBoardPostMutation();
  const resolveReport = useResolveAdminBoardReportMutation();
  const dismissReport = useDismissAdminBoardReportMutation();

  if (
    status === "loading" ||
    (status === "ok" && (posts.isPending || reports.isPending))
  ) {
    return <LoadingState message="Загрузка модерации…" />;
  }

  if (status !== "ok") {
    return (
      <ErrorState
        error="Недостаточно прав для модерации."
        backHref={routes.login}
        backLabel="Войти"
      />
    );
  }

  const loadError = posts.error ?? reports.error;
  const postItems = posts.data?.items ?? [];
  const reportItems = reports.data?.items ?? [];

  return (
    <div
      className="flex flex-col gap-8"
      data-testid="migration-board-moderation"
    >
      {loadError != null && (
        <ErrorState error={migrationBoardErrorMessage(loadError)} />
      )}
      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <Kicker>Записи на модерации</Kicker>
        {postItems.length === 0 ? (
          <EmptyState message="Нет записей на модерации." />
        ) : (
          postItems.map((post) => (
            <Card
              key={post.id}
              interactive={false}
              className="flex flex-col gap-3"
            >
              <span className="text-c4 text-xs">
                {post.author_display_name}
              </span>
              <span className="font-display text-lg font-semibold">
                {post.title}
              </span>
              <p className="text-c3 text-sm">{post.summary}</p>
              <div className="flex gap-3">
                <Button
                  onClick={() => approvePost.mutate(post.id)}
                  disabled={approvePost.isPending}
                  data-testid="migration-board-admin-approve"
                >
                  Approve
                </Button>
                <Button
                  variant="ghost"
                  onClick={() =>
                    rejectPost.mutate({
                      postId: post.id,
                      payload: { moderation_reason: "Rejected by moderator." },
                    })
                  }
                  disabled={rejectPost.isPending}
                >
                  Reject
                </Button>
                <Button
                  variant="ghost"
                  onClick={() =>
                    hidePost.mutate({
                      postId: post.id,
                      payload: { moderation_reason: "Hidden by moderator." },
                    })
                  }
                  disabled={hidePost.isPending}
                >
                  Hide
                </Button>
              </div>
            </Card>
          ))
        )}
      </Card>

      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <Kicker>Жалобы</Kicker>
        {reportItems.length === 0 ? (
          <p className="text-c3 text-sm">Нет жалоб.</p>
        ) : (
          reportItems.map((report) => (
            <div
              key={report.id}
              className="border-warm flex items-center justify-between gap-4 border-b py-3 last:border-b-0"
            >
              <span className="text-c2 text-sm">
                {report.reason}: {report.status}
              </span>
              <div className="flex gap-3">
                <Button
                  variant="ghost"
                  onClick={() =>
                    resolveReport.mutate({
                      reportId: report.id,
                      payload: {
                        resolution_note: "Resolved.",
                        hide_post: false,
                      },
                    })
                  }
                  disabled={resolveReport.isPending}
                >
                  Resolve
                </Button>
                <Button
                  variant="ghost"
                  onClick={() =>
                    dismissReport.mutate({
                      reportId: report.id,
                      payload: {
                        resolution_note: "Dismissed.",
                        hide_post: false,
                      },
                    })
                  }
                  disabled={dismissReport.isPending}
                >
                  Dismiss
                </Button>
              </div>
            </div>
          ))
        )}
      </Card>
    </div>
  );
}
