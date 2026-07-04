"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { isApiError } from "../../shared/api/http";
import { useAuth } from "../../shared/auth/AuthProvider";
import { routes } from "../../shared/lib/routes";

export function RegisterForm() {
  const { register } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);
    try {
      await register(email, password, displayName);
      router.push(routes.account);
    } catch (err: unknown) {
      if (isApiError(err)) {
        const code = err.error?.code;
        if (code === "email_already_registered") {
          setError("Аккаунт с таким email уже существует.");
        } else if (code === "weak_password") {
          setError(err.error?.message ?? "Пароль слишком короткий.");
        } else if (code === "invalid_email") {
          setError("Некорректный email.");
        } else if (code === "feature_disabled") {
          setError("Регистрация временно отключена.");
        } else {
          setError("Не удалось зарегистрироваться. Попробуйте ещё раз.");
        }
      } else {
        setError("Не удалось зарегистрироваться. Попробуйте ещё раз.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form
      className="authForm"
      onSubmit={handleSubmit}
      data-testid="register-form"
    >
      <label className="formGroup">
        <span className="formLabel">Email</span>
        <input
          type="email"
          className="formInput"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          required
          data-testid="register-email"
        />
      </label>
      <label className="formGroup">
        <span className="formLabel">Имя</span>
        <input
          type="text"
          className="formInput"
          value={displayName}
          onChange={(event) => setDisplayName(event.target.value)}
          required
          data-testid="register-display-name"
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
          minLength={12}
          data-testid="register-password"
        />
      </label>
      {error && (
        <p
          className="formError"
          data-testid="register-error"
        >
          {error}
        </p>
      )}
      <button
        type="submit"
        className="runButton"
        disabled={isSubmitting}
        data-testid="register-submit"
      >
        {isSubmitting ? "Регистрируем…" : "Зарегистрироваться"}
      </button>
      <p className="authFormFooter">
        Уже есть аккаунт? <Link href={routes.login}>Войти</Link>
      </p>
    </form>
  );
}
