"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  createContactRequest,
  getBoardPost,
  reportPost,
  type MigrationBoardPostDetail,
} from "../../shared/api";
import { useAuth } from "../../shared/auth/AuthProvider";
import { routes } from "../../shared/lib/routes";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";
import { migrationBoardErrorMessage } from "./errorMessage";

export function MigrationBoardDetailView({ postId }: { postId: string }) {
  const { user } = useAuth();
  const [post, setPost] = useState<MigrationBoardPostDetail | null>(null);
  const [message, setMessage] = useState("");
  const [reportDetails, setReportDetails] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<unknown | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let active = true;
    getBoardPost(postId)
      .then((response) => {
        if (active) setPost(response);
      })
      .catch((err: unknown) => {
        if (active) setError(err);
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });
    return () => {
      active = false;
    };
  }, [postId]);

  async function sendContactRequest() {
    setStatus(null);
    setError(null);
    try {
      await createContactRequest(postId, { message });
      setMessage("");
      setStatus("Contact request отправлен.");
    } catch (err: unknown) {
      setError(err);
    }
  }

  async function sendReport() {
    setStatus(null);
    setError(null);
    try {
      await reportPost(postId, {
        reason: "other",
        details: reportDetails || null,
      });
      setReportDetails("");
      setStatus("Жалоба отправлена на модерацию.");
    } catch (err: unknown) {
      setError(err);
    }
  }

  if (isLoading) {
    return <LoadingState message="Загрузка записи…" />;
  }

  if (error && !post) {
    return <ErrorState error={migrationBoardErrorMessage(error)} />;
  }

  if (!post) {
    return <ErrorState error="Запись не найдена." />;
  }

  return (
    <div
      className="searchPageContainer"
      data-testid="migration-board-detail"
    >
      {error !== null && (
        <ErrorState error={migrationBoardErrorMessage(error)} />
      )}
      {status && <p className="notice">{status}</p>}
      <section className="accountSection">
        <p className="eyebrow">{post.destination_country.name}</p>
        <h2>{post.title}</h2>
        <p>{post.summary}</p>
        <div className="badgeRow">
          <span className="badge">{post.author.display_name}</span>
          <span className="badge">{post.timeline_window}</span>
          <span className="badge">{post.migration_stage}</span>
          <span className="badge">{post.companion_goal}</span>
        </div>
        <p>
          Направление:{" "}
          <Link href={routes.country(post.destination_country.slug)}>
            {post.destination_country.name}
          </Link>
          {post.origin_country ? ` из ${post.origin_country.name}` : ""}
        </p>
        {post.route && (
          <p>
            Route:{" "}
            <Link href={`/routes/${post.route.id}`}>{post.route.title}</Link>
          </p>
        )}
        {(post.tags ?? []).length > 0 && (
          <div className="badgeRow">
            {(post.tags ?? []).map((tag) => (
              <span
                className="badge"
                key={tag}
              >
                {tag}
              </span>
            ))}
          </div>
        )}
      </section>

      <section className="accountSection">
        <p className="accountSectionTitle">Contact request</p>
        {!user ? (
          <p className="notice">
            <Link href={routes.login}>Войдите</Link>, чтобы отправить request
            через платформу.
          </p>
        ) : post.contact_requests_enabled ? (
          <>
            <textarea
              className="formInput"
              rows={4}
              minLength={20}
              maxLength={800}
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              placeholder="Коротко опишите, почему хотите связаться."
              data-testid="migration-board-contact-message"
            />
            <button
              type="button"
              className="runButton"
              onClick={() => void sendContactRequest()}
              disabled={message.length < 20}
              data-testid="migration-board-contact-submit"
            >
              Отправить request
            </button>
          </>
        ) : (
          <p className="notice">Автор отключил contact requests.</p>
        )}
      </section>

      <section className="accountSection">
        <p className="accountSectionTitle">Жалоба</p>
        {!user ? (
          <p className="notice">Жалобы доступны после входа.</p>
        ) : (
          <>
            <textarea
              className="formInput"
              rows={3}
              value={reportDetails}
              onChange={(event) => setReportDetails(event.target.value)}
              placeholder="Опишите проблему без персональных данных."
              data-testid="migration-board-report-message"
            />
            <button
              type="button"
              className="secondaryButton"
              onClick={() => void sendReport()}
              data-testid="migration-board-report-submit"
            >
              Пожаловаться
            </button>
          </>
        )}
      </section>
    </div>
  );
}
