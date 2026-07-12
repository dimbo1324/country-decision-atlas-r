"use client";

import { useEffect, useState } from "react";
import { Link, useRouter } from "../../i18n/navigation";
import {
  authApi,
  type AuthSession,
  type SecurityNotification,
  type TelegramLinkStatusResponse,
} from "../../shared/api/auth";
import { isApiError } from "../../shared/api/http";
import { useAuth } from "../../shared/auth/AuthProvider";
import { routes } from "../../shared/lib/routes";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";

export function AccountView() {
  const { user, isLoading, logout } = useAuth();
  const router = useRouter();
  const [sessions, setSessions] = useState<AuthSession[]>([]);
  const [notifications, setNotifications] = useState<SecurityNotification[]>(
    [],
  );
  const [telegramStatus, setTelegramStatus] =
    useState<TelegramLinkStatusResponse | null>(null);
  const [linkCode, setLinkCode] = useState("");
  const [telegramError, setTelegramError] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<unknown | null>(null);
  const [revokeAllPassword, setRevokeAllPassword] = useState("");
  const [revokeAllError, setRevokeAllError] = useState<string | null>(null);
  const [showRevokeAllConfirm, setShowRevokeAllConfirm] = useState(false);

  useEffect(() => {
    if (!user) return;
    let active = true;
    Promise.all([
      authApi.listSessions(),
      authApi.getTelegramLinkStatus(),
      authApi.listSecurityNotifications(),
    ])
      .then(([sessionResponse, linkStatus, notificationResponse]) => {
        if (!active) return;
        setSessions(sessionResponse.items ?? []);
        setTelegramStatus(linkStatus);
        setNotifications(notificationResponse.items ?? []);
      })
      .catch((err: unknown) => {
        if (active) setLoadError(err);
      });
    return () => {
      active = false;
    };
  }, [user]);

  async function handleLogout() {
    await logout();
    router.push(routes.home);
  }

  async function handleRevokeSession(sessionId: string) {
    await authApi.revokeSession(sessionId);
    setSessions((prev) => prev.filter((session) => session.id !== sessionId));
  }

  async function handleRevokeAll(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setRevokeAllError(null);
    try {
      await authApi.revokeAllSessions(revokeAllPassword);
      setSessions([]);
      setShowRevokeAllConfirm(false);
      setRevokeAllPassword("");
    } catch (err: unknown) {
      setRevokeAllError(
        isApiError(err)
          ? (err.error?.message ?? "Не удалось отозвать сессии.")
          : "Не удалось отозвать сессии.",
      );
    }
  }

  async function handleAcknowledgeNotification(notificationId: string) {
    await authApi.acknowledgeSecurityNotification(notificationId);
    setNotifications((prev) =>
      prev.filter((notification) => notification.id !== notificationId),
    );
  }

  async function handleLinkTelegram(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setTelegramError(null);
    try {
      const link = await authApi.linkTelegram(linkCode);
      setTelegramStatus({
        linked: true,
        telegram_user_id: link.telegram_user_id,
      });
      setLinkCode("");
    } catch (err: unknown) {
      if (isApiError(err)) {
        setTelegramError(
          err.error?.message ?? "Не удалось привязать Telegram.",
        );
      } else {
        setTelegramError("Не удалось привязать Telegram.");
      }
    }
  }

  async function handleUnlinkTelegram() {
    await authApi.unlinkTelegram();
    setTelegramStatus({ linked: false });
  }

  if (isLoading) {
    return <LoadingState message="Загрузка аккаунта…" />;
  }

  if (!user) {
    return (
      <div
        className="notice"
        data-testid="account-unauthenticated"
      >
        Войдите, чтобы просмотреть личный кабинет.{" "}
        <Link href={routes.login}>Войти</Link>
      </div>
    );
  }

  return (
    <div
      className="searchPageContainer"
      data-testid="account-view"
    >
      <div className="accountSection">
        <p className="accountSectionTitle">Профиль</p>
        <div className="accountField">
          <span className="accountFieldLabel">Email</span>
          <span data-testid="account-email">{user.email}</span>
        </div>
        <div className="accountField">
          <span className="accountFieldLabel">Имя</span>
          <span data-testid="account-display-name">{user.display_name}</span>
        </div>
        <div className="accountField">
          <span className="accountFieldLabel">Роль</span>
          <span data-testid="account-role">{user.role}</span>
        </div>
        <div className="accountField">
          <span className="accountFieldLabel">Статус</span>
          <span data-testid="account-status">{user.status}</span>
        </div>
        <button
          type="button"
          className="runButton"
          onClick={handleLogout}
        >
          Выйти
        </button>
      </div>

      {loadError !== null && (
        <ErrorState error={isApiError(loadError) ? loadError : undefined} />
      )}

      {notifications.length > 0 && (
        <div
          className="accountSection"
          data-testid="security-notifications"
        >
          <p className="accountSectionTitle">Уведомления безопасности</p>
          {notifications.map((notification) => (
            <div
              className="sessionRow"
              key={notification.id}
              data-testid="new-device-notification"
            >
              <span>
                Вход с нового устройства: {notification.device_label ?? "?"}
                {notification.ip_display ? ` (${notification.ip_display})` : ""}
                , {new Date(notification.created_at).toLocaleString("ru-RU")}.
                Это были вы?
              </span>
              <button
                type="button"
                className="runButton"
                onClick={() => handleAcknowledgeNotification(notification.id)}
              >
                Подтвердить
              </button>
            </div>
          ))}
        </div>
      )}

      <div className="accountSection">
        <p className="accountSectionTitle">Telegram</p>
        {telegramStatus?.linked ? (
          <>
            <p data-testid="telegram-linked-state">Telegram привязан.</p>
            <button
              type="button"
              className="runButton"
              onClick={handleUnlinkTelegram}
              data-testid="telegram-unlink-button"
            >
              Отвязать Telegram
            </button>
          </>
        ) : (
          <form
            onSubmit={handleLinkTelegram}
            className="authForm"
          >
            <label className="formGroup">
              <span className="formLabel">Код из /web_link</span>
              <input
                type="text"
                className="formInput"
                value={linkCode}
                onChange={(event) => setLinkCode(event.target.value)}
                required
                data-testid="telegram-link-code-input"
              />
            </label>
            {telegramError && <p className="formError">{telegramError}</p>}
            <button
              type="submit"
              className="runButton"
              data-testid="telegram-link-submit"
            >
              Привязать Telegram
            </button>
          </form>
        )}
      </div>

      <div className="accountSection">
        <p className="accountSectionTitle">Активные сессии</p>
        {sessions.length === 0 ? (
          <p className="notice">Нет активных сессий.</p>
        ) : (
          <div data-testid="session-list">
            {sessions.map((session) => (
              <div
                className="sessionRow"
                key={session.id}
              >
                <span>
                  {session.device_label ?? "Неизвестное устройство"}
                  {session.ip_display ? ` · ${session.ip_display}` : ""}
                  {" · "}
                  {new Date(session.created_at).toLocaleString("ru-RU")}
                  {session.is_current ? " · текущая сессия" : ""}
                </span>
                <button
                  type="button"
                  className="runButton"
                  onClick={() => handleRevokeSession(session.id)}
                >
                  Отозвать
                </button>
              </div>
            ))}
          </div>
        )}
        {showRevokeAllConfirm ? (
          <form
            onSubmit={handleRevokeAll}
            className="authForm"
          >
            <label className="formGroup">
              <span className="formLabel">Подтвердите пароль</span>
              <input
                type="password"
                className="formInput"
                value={revokeAllPassword}
                onChange={(event) => setRevokeAllPassword(event.target.value)}
                required
                data-testid="revoke-all-password-input"
              />
            </label>
            {revokeAllError && <p className="formError">{revokeAllError}</p>}
            <button
              type="submit"
              className="runButton"
              data-testid="revoke-all-confirm-submit"
            >
              Подтвердить отзыв всех сессий
            </button>
          </form>
        ) : (
          <button
            type="button"
            className="runButton"
            onClick={() => setShowRevokeAllConfirm(true)}
          >
            Отозвать все сессии
          </button>
        )}
      </div>
    </div>
  );
}
