"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  acceptContactRequest,
  archiveBoardPost,
  cancelContactRequest,
  declineContactRequest,
  listIncomingContactRequests,
  listMyBoardPosts,
  listOutgoingContactRequests,
  submitBoardPost,
  type ContactRequestListResponse,
  type MyMigrationBoardPostListResponse,
} from "../../shared/api";
import { useAuth } from "../../shared/auth/AuthProvider";
import { routes } from "../../shared/lib/routes";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";
import { migrationBoardErrorMessage } from "./errorMessage";

export function AccountMigrationBoardView() {
  const { user, isLoading: authLoading } = useAuth();
  const [posts, setPosts] = useState<MyMigrationBoardPostListResponse | null>(
    null,
  );
  const [incoming, setIncoming] = useState<ContactRequestListResponse | null>(
    null,
  );
  const [outgoing, setOutgoing] = useState<ContactRequestListResponse | null>(
    null,
  );
  const [error, setError] = useState<unknown | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  async function reload() {
    setError(null);
    const [postData, incomingData, outgoingData] = await Promise.all([
      listMyBoardPosts(),
      listIncomingContactRequests(),
      listOutgoingContactRequests(),
    ]);
    setPosts(postData);
    setIncoming(incomingData);
    setOutgoing(outgoingData);
  }

  useEffect(() => {
    if (!user) {
      setIsLoading(false);
      return;
    }
    setIsLoading(true);
    reload()
      .catch((err: unknown) => setError(err))
      .finally(() => setIsLoading(false));
  }, [user]);

  async function action(fn: () => Promise<unknown>) {
    setError(null);
    try {
      await fn();
      await reload();
    } catch (err: unknown) {
      setError(err);
    }
  }

  if (authLoading || isLoading) {
    return <LoadingState message="Загрузка migration board…" />;
  }

  if (!user) {
    return (
      <ErrorState
        error="Войдите, чтобы видеть свои записи."
        backHref={routes.login}
        backLabel="Войти"
      />
    );
  }

  return (
    <div
      className="searchPageContainer"
      data-testid="account-migration-board"
    >
      {error !== null && (
        <ErrorState error={migrationBoardErrorMessage(error)} />
      )}
      <div className="toolbar">
        <Link
          className="runButton"
          href={routes.migrationBoardNew}
        >
          Создать запись
        </Link>
        <Link
          className="secondaryButton"
          href={routes.migrationBoard}
        >
          Публичная доска
        </Link>
      </div>
      <section className="accountSection">
        <p className="accountSectionTitle">Мои записи</p>
        {(posts?.items ?? []).length === 0 ? (
          <EmptyState message="Записей пока нет." />
        ) : (
          <div className="cardGrid">
            {posts?.items.map((post) => (
              <div
                className="summaryCard"
                key={post.id}
              >
                <p className="eyebrow">{post.destination_country.name}</p>
                <h2>{post.title}</h2>
                <p>{post.summary}</p>
                <div className="badgeRow">
                  <span className="badge">{post.status}</span>
                  <span className="badge">{post.moderation_status}</span>
                </div>
                <div className="toolbar">
                  <button
                    type="button"
                    className="secondaryButton"
                    onClick={() => void action(() => submitBoardPost(post.id))}
                    disabled={
                      post.status === "review" || post.status === "published"
                    }
                    data-testid="migration-board-account-submit"
                  >
                    На модерацию
                  </button>
                  <button
                    type="button"
                    className="secondaryButton"
                    onClick={() => void action(() => archiveBoardPost(post.id))}
                    disabled={post.status === "archived"}
                  >
                    Архив
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
      <section className="accountSection">
        <p className="accountSectionTitle">Входящие requests</p>
        {(incoming?.items ?? []).length === 0 ? (
          <p className="notice">Нет входящих requests.</p>
        ) : (
          incoming?.items.map((request) => (
            <div
              className="sessionRow"
              key={request.id}
            >
              <span>
                {request.post_title} от {request.from_user_display_name}:{" "}
                {request.status}
              </span>
              <button
                type="button"
                className="secondaryButton"
                onClick={() =>
                  void action(() => acceptContactRequest(request.id))
                }
              >
                Accept
              </button>
              <button
                type="button"
                className="secondaryButton"
                onClick={() =>
                  void action(() => declineContactRequest(request.id))
                }
              >
                Decline
              </button>
            </div>
          ))
        )}
      </section>
      <section className="accountSection">
        <p className="accountSectionTitle">Исходящие requests</p>
        {(outgoing?.items ?? []).length === 0 ? (
          <p className="notice">Нет исходящих requests.</p>
        ) : (
          outgoing?.items.map((request) => (
            <div
              className="sessionRow"
              key={request.id}
            >
              <span>
                {request.post_title} для {request.to_user_display_name}:{" "}
                {request.status}
              </span>
              <button
                type="button"
                className="secondaryButton"
                onClick={() =>
                  void action(() => cancelContactRequest(request.id))
                }
                disabled={request.status !== "pending"}
              >
                Cancel
              </button>
            </div>
          ))
        )}
      </section>
    </div>
  );
}
