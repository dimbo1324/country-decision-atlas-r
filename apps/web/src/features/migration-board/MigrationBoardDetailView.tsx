"use client";

import { useQuery } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import { useState } from "react";
import { Badge, Button, Card, Kicker } from "@country-decision-atlas/ui";
import { Link } from "../../i18n/navigation";
import {
  boardPostQuery,
  useCreateContactRequestMutation,
  useReportPostMutation,
} from "../../entities/migration-board/api";
import { useAuth } from "../../shared/auth/AuthProvider";
import { useAppLocale } from "../../shared/lib/useAppLocale";
import { routes } from "../../shared/lib/routes";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";
import { migrationBoardErrorMessage } from "./errorMessage";

const textareaClass =
  "border-warm bg-bg2 text-c1 font-body border px-4 py-2.5 text-sm outline-none focus-visible:border-gold transition-colors duration-200";

export function MigrationBoardDetailView({ postId }: { postId: string }) {
  const t = useTranslations("migrationBoardDetail");
  const locale = useAppLocale();
  const { user } = useAuth();
  const post = useQuery(boardPostQuery(postId));
  const [message, setMessage] = useState("");
  const [reportDetails, setReportDetails] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const createContactRequest = useCreateContactRequestMutation();
  const reportPost = useReportPostMutation();

  async function sendContactRequest() {
    setStatus(null);
    try {
      await createContactRequest.mutateAsync({ postId, payload: { message } });
      setMessage("");
      setStatus(t("contactRequestSent"));
    } catch {
      // surfaced via createContactRequest.error below
    }
  }

  async function sendReport() {
    setStatus(null);
    try {
      await reportPost.mutateAsync({
        postId,
        payload: { reason: "other", details: reportDetails || null },
      });
      setReportDetails("");
      setStatus(t("reportSent"));
    } catch {
      // surfaced via reportPost.error below
    }
  }

  if (post.isPending) {
    return <LoadingState message={t("loadingPost")} />;
  }

  if (post.isError) {
    return (
      <ErrorState error={migrationBoardErrorMessage(post.error, locale)} />
    );
  }

  const detail = post.data;

  return (
    <div
      className="flex flex-col gap-6"
      data-testid="migration-board-detail"
    >
      {(createContactRequest.error ?? reportPost.error) != null && (
        <ErrorState
          error={migrationBoardErrorMessage(
            createContactRequest.error ?? reportPost.error,
            locale,
          )}
        />
      )}
      {status && <p className="text-c3 text-sm">{status}</p>}

      <Card
        interactive={false}
        className="flex flex-col gap-3"
      >
        <Kicker>{detail.destination_country.name}</Kicker>
        <h2 className="font-display text-2xl font-semibold">{detail.title}</h2>
        <p className="text-c3 text-sm">{detail.summary}</p>
        <div className="flex flex-wrap gap-2">
          <Badge variant="default">{detail.author.display_name}</Badge>
          <Badge variant="default">{detail.timeline_window}</Badge>
          <Badge variant="default">{detail.migration_stage}</Badge>
          <Badge variant="default">{detail.companion_goal}</Badge>
        </div>
        <p className="text-c3 text-sm">
          {t("destinationLabel")}{" "}
          <Link
            href={routes.country(detail.destination_country.slug)}
            className="text-gold3 hover:text-gold"
          >
            {detail.destination_country.name}
          </Link>
          {detail.origin_country
            ? t("originSuffix", { country: detail.origin_country.name })
            : ""}
        </p>
        {detail.route && (
          <p className="text-c3 text-sm">
            {t("routeLabel")}{" "}
            <Link
              href={`/routes/${detail.route.id}`}
              className="text-gold3 hover:text-gold"
            >
              {detail.route.title}
            </Link>
          </p>
        )}
        {(detail.tags ?? []).length > 0 && (
          <div className="flex flex-wrap gap-2">
            {(detail.tags ?? []).map((tag) => (
              <Badge
                key={tag}
                variant="default"
              >
                {tag}
              </Badge>
            ))}
          </div>
        )}
      </Card>

      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <Kicker>{t("contactRequestKicker")}</Kicker>
        {!user ? (
          <p className="text-c3 text-sm">
            <Link
              href={routes.login}
              className="text-gold3 hover:text-gold"
            >
              {t("loginToContact")}
            </Link>
            {t("loginToContactSuffix")}
          </p>
        ) : detail.contact_requests_enabled ? (
          <>
            <textarea
              className={textareaClass}
              rows={4}
              minLength={20}
              maxLength={800}
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              placeholder={t("contactPlaceholder")}
              data-testid="migration-board-contact-message"
            />
            <p className="text-c4 text-xs">{t("contactPrivacyNotice")}</p>
            <Button
              onClick={() => void sendContactRequest()}
              disabled={message.length < 20 || createContactRequest.isPending}
              data-testid="migration-board-contact-submit"
            >
              {t("sendRequest")}
            </Button>
          </>
        ) : (
          <p className="text-c3 text-sm">{t("contactDisabled")}</p>
        )}
      </Card>

      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <Kicker>{t("reportKicker")}</Kicker>
        {!user ? (
          <p className="text-c3 text-sm">{t("reportLoginRequired")}</p>
        ) : (
          <>
            <textarea
              className={textareaClass}
              rows={3}
              value={reportDetails}
              onChange={(event) => setReportDetails(event.target.value)}
              placeholder={t("reportPlaceholder")}
              data-testid="migration-board-report-message"
            />
            <Button
              variant="ghost"
              onClick={() => void sendReport()}
              disabled={reportPost.isPending}
              data-testid="migration-board-report-submit"
            >
              {t("reportSubmit")}
            </Button>
          </>
        )}
      </Card>
    </div>
  );
}
