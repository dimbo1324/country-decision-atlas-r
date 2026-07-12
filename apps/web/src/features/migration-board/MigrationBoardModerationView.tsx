"use client";

import { useEffect, useState } from "react";
import {
  approveAdminBoardPost,
  dismissAdminBoardReport,
  hideAdminBoardPost,
  listAdminBoardPosts,
  listAdminBoardReports,
  rejectAdminBoardPost,
  resolveAdminBoardReport,
  type AdminMigrationBoardPostListResponse,
  type MigrationBoardReportListResponse,
} from "../../shared/api";
import { MODERATION_ROLES } from "../../shared/auth/roles";
import { useAuthGuard } from "../../shared/auth/useAuthGuard";
import { routes } from "../../shared/lib/routes";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";
import { migrationBoardErrorMessage } from "./errorMessage";

export function MigrationBoardModerationView() {
  const { status } = useAuthGuard(MODERATION_ROLES);
  const [posts, setPosts] =
    useState<AdminMigrationBoardPostListResponse | null>(null);
  const [reports, setReports] =
    useState<MigrationBoardReportListResponse | null>(null);
  const [error, setError] = useState<unknown | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  async function reload() {
    const [postData, reportData] = await Promise.all([
      listAdminBoardPosts("review"),
      listAdminBoardReports(),
    ]);
    setPosts(postData);
    setReports(reportData);
  }

  useEffect(() => {
    if (status !== "ok") {
      setIsLoading(false);
      return;
    }
    reload()
      .catch((err: unknown) => setError(err))
      .finally(() => setIsLoading(false));
  }, [status]);

  async function action(fn: () => Promise<unknown>) {
    setError(null);
    try {
      await fn();
      await reload();
    } catch (err: unknown) {
      setError(err);
    }
  }

  if (status === "loading" || (status === "ok" && isLoading)) {
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

  return (
    <div
      className="searchPageContainer"
      data-testid="migration-board-moderation"
    >
      {error !== null && (
        <ErrorState error={migrationBoardErrorMessage(error)} />
      )}
      <section className="accountSection">
        <p className="accountSectionTitle">Записи на модерации</p>
        {(posts?.items ?? []).length === 0 ? (
          <EmptyState message="Нет записей на модерации." />
        ) : (
          posts?.items.map((post) => (
            <div
              className="summaryCard"
              key={post.id}
            >
              <p className="eyebrow">{post.author_display_name}</p>
              <h2>{post.title}</h2>
              <p>{post.summary}</p>
              <div className="toolbar">
                <button
                  type="button"
                  className="runButton"
                  onClick={() =>
                    void action(() => approveAdminBoardPost(post.id))
                  }
                  data-testid="migration-board-admin-approve"
                >
                  Approve
                </button>
                <button
                  type="button"
                  className="secondaryButton"
                  onClick={() =>
                    void action(() =>
                      rejectAdminBoardPost(post.id, {
                        moderation_reason: "Rejected by moderator.",
                      }),
                    )
                  }
                >
                  Reject
                </button>
                <button
                  type="button"
                  className="secondaryButton"
                  onClick={() =>
                    void action(() =>
                      hideAdminBoardPost(post.id, {
                        moderation_reason: "Hidden by moderator.",
                      }),
                    )
                  }
                >
                  Hide
                </button>
              </div>
            </div>
          ))
        )}
      </section>
      <section className="accountSection">
        <p className="accountSectionTitle">Жалобы</p>
        {(reports?.items ?? []).length === 0 ? (
          <p className="notice">Нет жалоб.</p>
        ) : (
          reports?.items.map((report) => (
            <div
              className="sessionRow"
              key={report.id}
            >
              <span>
                {report.reason}: {report.status}
              </span>
              <button
                type="button"
                className="secondaryButton"
                onClick={() =>
                  void action(() =>
                    resolveAdminBoardReport(report.id, {
                      resolution_note: "Resolved.",
                      hide_post: false,
                    }),
                  )
                }
              >
                Resolve
              </button>
              <button
                type="button"
                className="secondaryButton"
                onClick={() =>
                  void action(() =>
                    dismissAdminBoardReport(report.id, {
                      resolution_note: "Dismissed.",
                      hide_post: false,
                    }),
                  )
                }
              >
                Dismiss
              </button>
            </div>
          ))
        )}
      </section>
    </div>
  );
}
