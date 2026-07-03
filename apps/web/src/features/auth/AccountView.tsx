"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import {
  authApi,
  type AuthSession,
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
  const [telegramStatus, setTelegramStatus] =
    useState<TelegramLinkStatusResponse | null>(null);
  const [linkCode, setLinkCode] = useState("");
  const [telegramError, setTelegramError] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<unknown | null>(null);

  useEffect(() => {
    if (!user) return;
    let active = true;
    Promise.all([authApi.listSessions(), authApi.getTelegramLinkStatus()])
      .then(([sessionResponse, linkStatus]) => {
        if (!active) return;
        setSessions(sessionResponse.items ?? []);
        setTelegramStatus(linkStatus);
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

  async function handleRevokeAll() {
    await authApi.revokeAllSessions();
    setSessions([]);
  }

  async function handleLinkTelegram(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setTelegramError(null);
    try {
      const link = await authApi.linkTelegram(linkCode);
      setTelegramStatus({ linked: true, telegram_user_id: link.telegram_user_id });
      setLinkCode("");
    } catch (err: unknown) {
      if (isApiError(err)) {
        setTelegramError(err.error?.message ?? "Не удалось привязать Telegram.");
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
      <div className="notice" data-testid="account-unauthenticated">
        Войдите, чтобы просмотреть личный кабинет.{" "}
        <Link href={routes.login}>Войти</Link>
      </div>
    );
  }

  return (
    <div className="searchPageContainer" data-testid="account-view">
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
        <button type="button" className="runButton" onClick={handleLogout}>
          Выйти
        </button>
      </div>

      {loadError !== null && (
        <ErrorState error={isApiError(loadError) ? loadError : undefined} />
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
          <form onSubmit={handleLinkTelegram} className="authForm">
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
              <div className="sessionRow" key={session.id}>
                <span>
                  Создана: {new Date(session.created_at).toLocaleString("ru-RU")}
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
        <button type="button" className="runButton" onClick={handleRevokeAll}>
          Отозвать все сессии
        </button>
      </div>
    </div>
  );
}
