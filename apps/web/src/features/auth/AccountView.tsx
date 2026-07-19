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
  Dialog,
  DialogClose,
  DialogContent,
  DialogTrigger,
  DataTable,
  Field,
  FieldError,
  FieldLabel,
  Kicker,
  toast,
} from "@country-decision-atlas/ui";
import { useState } from "react";
import { Link, useRouter } from "../../i18n/navigation";
import {
  sessionsQuery,
  securityNotificationsQuery,
  telegramStatusQuery,
  useAcknowledgeSecurityNotificationMutation,
  useLinkTelegramMutation,
  useRevokeAllSessionsMutation,
  useRevokeSessionMutation,
  useUnlinkTelegramMutation,
} from "../../entities/account/api";
import { isApiError } from "../../shared/api/http";
import { useAuth } from "../../shared/auth/AuthProvider";
import { routes } from "../../shared/lib/routes";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";
import { formatDateTime } from "../../shared/lib/format";
import { useAppLocale } from "../../shared/lib/useAppLocale";

const inputClass =
  "border-warm bg-bg2 text-c1 font-body border px-4 py-2.5 text-sm outline-none focus-visible:border-gold transition-colors duration-200";

function TelegramLinkForm() {
  const t = useTranslations("account");
  const linkTelegram = useLinkTelegramMutation();
  const telegramLinkSchema = z.object({
    code: z.string().min(1, t("telegramCodeRequired")),
  });
  type TelegramLinkValues = z.infer<typeof telegramLinkSchema>;
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<TelegramLinkValues>({
    resolver: zodResolver(telegramLinkSchema),
  });

  async function onSubmit(values: TelegramLinkValues) {
    try {
      await linkTelegram.mutateAsync(values.code);
      reset();
      toast.success(t("telegramLinked"));
    } catch (err: unknown) {
      toast.error(
        isApiError(err)
          ? (err.error?.message ?? t("telegramLinkError"))
          : t("telegramLinkError"),
      );
    }
  }

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="flex max-w-sm flex-col gap-4"
      noValidate
    >
      <Field>
        <FieldLabel htmlFor="telegram-link-code">
          {t("telegramCodeLabel")}
        </FieldLabel>
        <input
          id="telegram-link-code"
          type="text"
          className={inputClass}
          data-testid="telegram-link-code-input"
          {...register("code")}
        />
        <FieldError>{errors.code?.message}</FieldError>
      </Field>
      <Button
        type="submit"
        disabled={linkTelegram.isPending}
        data-testid="telegram-link-submit"
      >
        {linkTelegram.isPending ? t("linking") : t("linkTelegram")}
      </Button>
    </form>
  );
}

function RevokeAllSessionsDialog() {
  const t = useTranslations("account");
  const [open, setOpen] = useState(false);
  const revokeAll = useRevokeAllSessionsMutation();
  const revokeAllSchema = z.object({
    currentPassword: z.string().min(1, t("passwordRequired")),
  });
  type RevokeAllValues = z.infer<typeof revokeAllSchema>;
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<RevokeAllValues>({ resolver: zodResolver(revokeAllSchema) });

  async function onSubmit(values: RevokeAllValues) {
    try {
      await revokeAll.mutateAsync(values.currentPassword);
      reset();
      setOpen(false);
      toast.success(t("allSessionsRevoked"));
    } catch (err: unknown) {
      toast.error(
        isApiError(err)
          ? (err.error?.message ?? t("revokeError"))
          : t("revokeError"),
      );
    }
  }

  return (
    <Dialog
      open={open}
      onOpenChange={setOpen}
    >
      <DialogTrigger asChild>
        <Button
          variant="ghost"
          className="text-terra3 hover:text-terra2"
        >
          {t("revokeAllSessions")}
        </Button>
      </DialogTrigger>
      <DialogContent
        title={t("revokeAllSessions")}
        description={t("revokeAllDescription")}
      >
        <form
          onSubmit={handleSubmit(onSubmit)}
          className="flex flex-col gap-4"
          noValidate
        >
          <Field>
            <FieldLabel htmlFor="revoke-all-password">
              {t("password")}
            </FieldLabel>
            <input
              id="revoke-all-password"
              type="password"
              className={inputClass}
              data-testid="revoke-all-password-input"
              {...register("currentPassword")}
            />
            <FieldError>{errors.currentPassword?.message}</FieldError>
          </Field>
          <div className="flex gap-3">
            <Button
              type="submit"
              disabled={revokeAll.isPending}
              data-testid="revoke-all-confirm-submit"
            >
              {revokeAll.isPending ? t("revoking") : t("confirmRevokeAll")}
            </Button>
            <DialogClose asChild>
              <Button variant="ghost">{t("cancel")}</Button>
            </DialogClose>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export function AccountView() {
  const t = useTranslations("account");
  const locale = useAppLocale();
  const { user, isLoading, logout } = useAuth();
  const router = useRouter();

  const sessions = useQuery({ ...sessionsQuery(), enabled: Boolean(user) });
  const notifications = useQuery({
    ...securityNotificationsQuery(),
    enabled: Boolean(user),
  });
  const telegramStatus = useQuery({
    ...telegramStatusQuery(),
    enabled: Boolean(user),
  });

  const revokeSession = useRevokeSessionMutation();
  const acknowledgeNotification = useAcknowledgeSecurityNotificationMutation();
  const unlinkTelegram = useUnlinkTelegramMutation();

  async function handleLogout() {
    await logout();
    router.push(routes.home);
  }

  if (isLoading) {
    return <LoadingState message={t("loadingAccount")} />;
  }

  if (!user) {
    return (
      <div
        className="border-warm flex flex-col gap-2 border px-4 py-4"
        data-testid="account-unauthenticated"
      >
        <p className="text-c3 text-sm">
          {t("loginToView")}{" "}
          <Link
            href={routes.login}
            className="text-c1 hover:text-gold3 underline decoration-dotted underline-offset-2 transition-colors duration-200"
          >
            {t("login")}
          </Link>
        </p>
      </div>
    );
  }

  const loadError =
    sessions.error ?? notifications.error ?? telegramStatus.error;
  const sessionItems = sessions.data?.items ?? [];
  const notificationItems = notifications.data?.items ?? [];

  return (
    <div
      className="flex flex-col gap-8"
      data-testid="account-view"
    >
      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <Kicker>{t("profile")}</Kicker>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <div className="flex flex-col gap-1">
            <span className="text-c4 text-xs">{t("email")}</span>
            <span data-testid="account-email">{user.email}</span>
          </div>
          <div className="flex flex-col gap-1">
            <span className="text-c4 text-xs">{t("name")}</span>
            <span data-testid="account-display-name">{user.display_name}</span>
          </div>
          <div className="flex flex-col gap-1">
            <span className="text-c4 text-xs">{t("role")}</span>
            <span data-testid="account-role">{user.role}</span>
          </div>
          <div className="flex flex-col gap-1">
            <span className="text-c4 text-xs">{t("status")}</span>
            <span data-testid="account-status">{user.status}</span>
          </div>
        </div>
        <Button
          variant="ghost"
          onClick={handleLogout}
        >
          {t("logout")}
        </Button>
      </Card>

      {loadError !== null && loadError !== undefined && (
        <ErrorState error={isApiError(loadError) ? loadError : undefined} />
      )}

      {notificationItems.length > 0 && (
        <div data-testid="security-notifications">
          <Card
            interactive={false}
            className="flex flex-col gap-3"
          >
            <Kicker>{t("securityNotifications")}</Kicker>
            {notificationItems.map((notification) => (
              <div
                key={notification.id}
                className="border-warm flex items-center justify-between gap-4 border-b pb-3 last:border-b-0 last:pb-0"
                data-testid="new-device-notification"
              >
                <span className="text-c2 text-sm">
                  {t("newDeviceLogin", {
                    device: notification.device_label ?? "?",
                    ip: notification.ip_display
                      ? ` (${notification.ip_display})`
                      : "",
                    date: formatDateTime(notification.created_at, locale),
                  })}
                </span>
                <Button
                  variant="ghost"
                  onClick={() =>
                    acknowledgeNotification.mutate(notification.id)
                  }
                >
                  {t("confirm")}
                </Button>
              </div>
            ))}
          </Card>
        </div>
      )}

      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <Kicker>Telegram</Kicker>
        {telegramStatus.data?.linked ? (
          <div className="flex items-center gap-4">
            <span data-testid="telegram-linked-state">
              <Badge variant="default">{t("telegramLinkedBadge")}</Badge>
            </span>
            <Button
              variant="ghost"
              onClick={() => unlinkTelegram.mutate()}
              data-testid="telegram-unlink-button"
            >
              {t("unlinkTelegram")}
            </Button>
          </div>
        ) : (
          <TelegramLinkForm />
        )}
      </Card>

      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <Kicker>{t("activeSessions")}</Kicker>
        {sessionItems.length === 0 ? (
          <p className="text-c3 text-sm">{t("noActiveSessions")}</p>
        ) : (
          <div data-testid="session-list">
            <DataTable
              columns={[
                { header: t("device") },
                { header: t("date") },
                { header: "" },
              ]}
              rows={sessionItems.map((session) => [
                <span key="device">
                  {session.device_label ?? t("unknownDevice")}
                  {session.ip_display ? ` · ${session.ip_display}` : ""}
                  {session.is_current ? ` · ${t("currentSession")}` : ""}
                </span>,
                <span key="date">
                  {formatDateTime(session.created_at, locale)}
                </span>,
                <Button
                  key="revoke"
                  variant="ghost"
                  onClick={() => revokeSession.mutate(session.id)}
                >
                  {t("revoke")}
                </Button>,
              ])}
            />
          </div>
        )}
        <div>
          <RevokeAllSessionsDialog />
        </div>
      </Card>
    </div>
  );
}
