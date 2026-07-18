"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useQuery } from "@tanstack/react-query";
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

const telegramLinkSchema = z.object({
  code: z.string().min(1, "Введите код из /web_link"),
});
type TelegramLinkValues = z.infer<typeof telegramLinkSchema>;

const revokeAllSchema = z.object({
  currentPassword: z.string().min(1, "Введите пароль"),
});
type RevokeAllValues = z.infer<typeof revokeAllSchema>;

function TelegramLinkForm() {
  const linkTelegram = useLinkTelegramMutation();
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
      toast.success("Telegram привязан.");
    } catch (err: unknown) {
      toast.error(
        isApiError(err)
          ? (err.error?.message ?? "Не удалось привязать Telegram.")
          : "Не удалось привязать Telegram.",
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
        <FieldLabel htmlFor="telegram-link-code">Код из /web_link</FieldLabel>
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
        {linkTelegram.isPending ? "Привязываем…" : "Привязать Telegram"}
      </Button>
    </form>
  );
}

function RevokeAllSessionsDialog() {
  const [open, setOpen] = useState(false);
  const revokeAll = useRevokeAllSessionsMutation();
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
      toast.success("Все сессии отозваны.");
    } catch (err: unknown) {
      toast.error(
        isApiError(err)
          ? (err.error?.message ?? "Не удалось отозвать сессии.")
          : "Не удалось отозвать сессии.",
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
          Отозвать все сессии
        </Button>
      </DialogTrigger>
      <DialogContent
        title="Отозвать все сессии"
        description="Это действие завершит все активные сессии, включая текущую. Подтвердите пароль."
      >
        <form
          onSubmit={handleSubmit(onSubmit)}
          className="flex flex-col gap-4"
          noValidate
        >
          <Field>
            <FieldLabel htmlFor="revoke-all-password">Пароль</FieldLabel>
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
              {revokeAll.isPending
                ? "Отзываем…"
                : "Подтвердить отзыв всех сессий"}
            </Button>
            <DialogClose asChild>
              <Button variant="ghost">Отмена</Button>
            </DialogClose>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export function AccountView() {
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
    return <LoadingState message="Загрузка аккаунта…" />;
  }

  if (!user) {
    return (
      <div
        className="border-warm flex flex-col gap-2 border px-4 py-4"
        data-testid="account-unauthenticated"
      >
        <p className="text-c3 text-sm">
          Войдите, чтобы просмотреть личный кабинет.{" "}
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
        <Kicker>Профиль</Kicker>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <div className="flex flex-col gap-1">
            <span className="text-c4 text-xs">Email</span>
            <span data-testid="account-email">{user.email}</span>
          </div>
          <div className="flex flex-col gap-1">
            <span className="text-c4 text-xs">Имя</span>
            <span data-testid="account-display-name">{user.display_name}</span>
          </div>
          <div className="flex flex-col gap-1">
            <span className="text-c4 text-xs">Роль</span>
            <span data-testid="account-role">{user.role}</span>
          </div>
          <div className="flex flex-col gap-1">
            <span className="text-c4 text-xs">Статус</span>
            <span data-testid="account-status">{user.status}</span>
          </div>
        </div>
        <Button
          variant="ghost"
          onClick={handleLogout}
        >
          Выйти
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
            <Kicker>Уведомления безопасности</Kicker>
            {notificationItems.map((notification) => (
              <div
                key={notification.id}
                className="border-warm flex items-center justify-between gap-4 border-b pb-3 last:border-b-0 last:pb-0"
                data-testid="new-device-notification"
              >
                <span className="text-c2 text-sm">
                  Вход с нового устройства: {notification.device_label ?? "?"}
                  {notification.ip_display
                    ? ` (${notification.ip_display})`
                    : ""}
                  , {formatDateTime(notification.created_at, locale)}. Это были
                  вы?
                </span>
                <Button
                  variant="ghost"
                  onClick={() =>
                    acknowledgeNotification.mutate(notification.id)
                  }
                >
                  Подтвердить
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
              <Badge variant="default">Telegram привязан</Badge>
            </span>
            <Button
              variant="ghost"
              onClick={() => unlinkTelegram.mutate()}
              data-testid="telegram-unlink-button"
            >
              Отвязать Telegram
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
        <Kicker>Активные сессии</Kicker>
        {sessionItems.length === 0 ? (
          <p className="text-c3 text-sm">Нет активных сессий.</p>
        ) : (
          <div data-testid="session-list">
            <DataTable
              columns={[
                { header: "Устройство" },
                { header: "Дата" },
                { header: "" },
              ]}
              rows={sessionItems.map((session) => [
                <span key="device">
                  {session.device_label ?? "Неизвестное устройство"}
                  {session.ip_display ? ` · ${session.ip_display}` : ""}
                  {session.is_current ? " · текущая сессия" : ""}
                </span>,
                <span key="date">
                  {formatDateTime(session.created_at, locale)}
                </span>,
                <Button
                  key="revoke"
                  variant="ghost"
                  onClick={() => revokeSession.mutate(session.id)}
                >
                  Отозвать
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
