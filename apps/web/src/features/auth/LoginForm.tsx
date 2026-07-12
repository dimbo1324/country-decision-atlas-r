"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import {
  Button,
  Field,
  FieldError,
  FieldLabel,
} from "@country-decision-atlas/ui";
import { useTranslations } from "next-intl";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Link, useRouter } from "../../i18n/navigation";
import { isApiError } from "../../shared/api/http";
import { useAuth } from "../../shared/auth/AuthProvider";
import { routes } from "../../shared/lib/routes";

const loginSchema = z.object({
  email: z.string().min(1, "emailRequired").email("emailInvalid"),
  password: z.string().min(1, "passwordRequired"),
});
type LoginFormValues = z.infer<typeof loginSchema>;

const inputClass =
  "border-warm bg-bg2 text-c1 font-body border px-4 py-2.5 text-sm outline-none focus-visible:border-gold transition-colors duration-200";

export function LoginForm() {
  const t = useTranslations("auth");
  const { login } = useAuth();
  const router = useRouter();
  const [submitError, setSubmitError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormValues>({ resolver: zodResolver(loginSchema) });

  async function onSubmit(values: LoginFormValues) {
    setSubmitError(null);
    try {
      await login(values.email, values.password);
      router.push(routes.account);
    } catch (err: unknown) {
      if (isApiError(err)) {
        setSubmitError(
          err.error?.code === "feature_disabled"
            ? t("loginErrorDisabled")
            : t("loginErrorDefault"),
        );
      } else {
        setSubmitError(t("loginErrorGeneric"));
      }
    }
  }

  return (
    <form
      className="flex max-w-sm flex-col gap-5"
      onSubmit={handleSubmit(onSubmit)}
      data-testid="login-form"
      noValidate
    >
      <Field>
        <FieldLabel htmlFor="login-email">{t("email")}</FieldLabel>
        <input
          id="login-email"
          type="email"
          className={inputClass}
          data-testid="login-email"
          {...register("email")}
        />
        <FieldError>
          {errors.email && t(errors.email.message as Parameters<typeof t>[0])}
        </FieldError>
      </Field>
      <Field>
        <FieldLabel htmlFor="login-password">{t("password")}</FieldLabel>
        <input
          id="login-password"
          type="password"
          className={inputClass}
          data-testid="login-password"
          {...register("password")}
        />
        <FieldError>
          {errors.password &&
            t(errors.password.message as Parameters<typeof t>[0])}
        </FieldError>
      </Field>
      {submitError && (
        <p
          className="font-quote text-terra3 text-sm italic"
          data-testid="login-error"
        >
          {submitError}
        </p>
      )}
      <Button
        type="submit"
        disabled={isSubmitting}
        data-testid="login-submit"
      >
        {isSubmitting ? t("loginSubmitting") : t("loginSubmit")}
      </Button>
      <p className="text-c3 text-sm">
        {t("noAccount")}{" "}
        <Link
          href={routes.register}
          className="text-gold3 hover:text-gold"
        >
          {t("registerLink")}
        </Link>
      </p>
    </form>
  );
}
