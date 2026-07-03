"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { isApiError } from "../../shared/api/http";
import { useAuth } from "../../shared/auth/AuthProvider";
import { routes } from "../../shared/lib/routes";

export function LoginForm() {
  const { login } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);
    try {
      await login(email, password);
      router.push(routes.account);
    } catch (err: unknown) {
      if (isApiError(err)) {
        const code = err.error?.code;
        if (code === "feature_disabled") {
          setError("Авторизация временно отключена.");
        } else {
          setError("Неверный email или пароль.");
        }
      } else {
        setError("Не удалось войти. Попробуйте ещё раз.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form className="authForm" onSubmit={handleSubmit} data-testid="login-form">
      <label className="formGroup">
        <span className="formLabel">Email</span>
        <input
          type="email"
          className="formInput"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          required
          data-testid="login-email"
        />
      </label>
      <label className="formGroup">
        <span className="formLabel">Пароль</span>
        <input
          type="password"
          className="formInput"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          required
          data-testid="login-password"
        />
      </label>
      {error && (
        <p className="formError" data-testid="login-error">
          {error}
        </p>
      )}
      <button
        type="submit"
        className="runButton"
        disabled={isSubmitting}
        data-testid="login-submit"
      >
        {isSubmitting ? "Входим…" : "Войти"}
      </button>
      <p className="authFormFooter">
        Нет аккаунта? <Link href={routes.register}>Зарегистрироваться</Link>
      </p>
    </form>
  );
}
