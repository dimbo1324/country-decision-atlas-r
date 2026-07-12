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

const registerSchema = z.object({
  email: z.string().min(1, "emailRequired").email("emailInvalid"),
  displayName: z.string().min(1, "displayNameRequired"),
  password: z.string().min(12, "passwordTooShort"),
});
type RegisterFormValues = z.infer<typeof registerSchema>;

const inputClass =
  "border-warm bg-bg2 text-c1 font-body border px-4 py-2.5 text-sm outline-none focus-visible:border-gold transition-colors duration-200";

export function RegisterForm() {
  const t = useTranslations("auth");
  const { register: registerUser } = useAuth();
  const router = useRouter();
  const [submitError, setSubmitError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormValues>({ resolver: zodResolver(registerSchema) });

  async function onSubmit(values: RegisterFormValues) {
    setSubmitError(null);
    try {
      await registerUser(values.email, values.password, values.displayName);
      router.push(routes.account);
    } catch (err: unknown) {
      if (isApiError(err)) {
        const code = err.error?.code;
        if (code === "email_already_registered") {
          setSubmitError(t("registerErrorEmailTaken"));
        } else if (code === "weak_password") {
          setSubmitError(err.error?.message ?? t("registerErrorWeakPassword"));
        } else if (code === "invalid_email") {
          setSubmitError(t("registerErrorInvalidEmail"));
        } else if (code === "feature_disabled") {
          setSubmitError(t("registerErrorDisabled"));
        } else {
          setSubmitError(t("registerErrorGeneric"));
        }
      } else {
        setSubmitError(t("registerErrorGeneric"));
      }
    }
  }

  return (
    <form
      className="flex max-w-sm flex-col gap-5"
      onSubmit={handleSubmit(onSubmit)}
      data-testid="register-form"
      noValidate
    >
      <Field>
        <FieldLabel htmlFor="register-email">{t("email")}</FieldLabel>
        <input
          id="register-email"
          type="email"
          className={inputClass}
          data-testid="register-email"
          {...register("email")}
        />
        <FieldError>
          {errors.email && t(errors.email.message as Parameters<typeof t>[0])}
        </FieldError>
      </Field>
      <Field>
        <FieldLabel htmlFor="register-display-name">
          {t("displayName")}
        </FieldLabel>
        <input
          id="register-display-name"
          type="text"
          className={inputClass}
          data-testid="register-display-name"
          {...register("displayName")}
        />
        <FieldError>
          {errors.displayName &&
            t(errors.displayName.message as Parameters<typeof t>[0])}
        </FieldError>
      </Field>
      <Field>
        <FieldLabel htmlFor="register-password">{t("password")}</FieldLabel>
        <input
          id="register-password"
          type="password"
          className={inputClass}
          data-testid="register-password"
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
          data-testid="register-error"
        >
          {submitError}
        </p>
      )}
      <Button
        type="submit"
        disabled={isSubmitting}
        data-testid="register-submit"
      >
        {isSubmitting ? t("registerSubmitting") : t("registerSubmit")}
      </Button>
      <p className="text-c3 text-sm">
        {t("hasAccount")}{" "}
        <Link
          href={routes.login}
          className="text-gold3 hover:text-gold"
        >
          {t("loginLink")}
        </Link>
      </p>
    </form>
  );
}
