"use client";

import { FormEvent, useState } from "react";
import { useTranslations } from "next-intl";
import { Button, Field, FieldLabel } from "@country-decision-atlas/ui";
import { useAskAIMutation } from "../../entities/ai-assistant/api";
import type { AIAskResponse } from "../../shared/api/ai";
import { isApiError } from "../../shared/api";
import { toApiLocale, type SupportedLocale } from "../../shared/lib/locale";

const inputClass =
  "border-warm bg-bg2 text-c1 font-body border px-4 py-2.5 text-sm outline-none focus-visible:border-gold transition-colors duration-200";

type AIAskFormProps = {
  locale: SupportedLocale;
  onResponse: (response: AIAskResponse) => void;
  onPendingChange?: (pending: boolean) => void;
};

export function AIAskForm({
  locale,
  onResponse,
  onPendingChange,
}: AIAskFormProps) {
  const t = useTranslations("aiAskForm");
  const [question, setQuestion] = useState(t("defaultQuestion"));
  const [countrySlug, setCountrySlug] = useState("uruguay");
  const askAI = useAskAIMutation();

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onPendingChange?.(true);
    try {
      const response = await askAI.mutateAsync({
        question,
        locale: toApiLocale(locale),
        country_slug: countrySlug || undefined,
      });
      onResponse(response);
    } catch {
      // handled by askAI.isError below
    } finally {
      onPendingChange?.(false);
    }
  }

  return (
    <form
      className="flex flex-col gap-4"
      onSubmit={handleSubmit}
      data-testid="ai-ask-form"
    >
      <Field>
        <FieldLabel htmlFor="ai-question">{t("questionLabel")}</FieldLabel>
        <textarea
          id="ai-question"
          className={inputClass}
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          data-testid="ai-question-input"
          rows={4}
        />
      </Field>
      <Field>
        <FieldLabel htmlFor="ai-country">{t("countryLabel")}</FieldLabel>
        <input
          id="ai-country"
          className={inputClass}
          value={countrySlug}
          onChange={(event) => setCountrySlug(event.target.value)}
          data-testid="ai-country-input"
        />
      </Field>
      {askAI.isError && (
        <p
          className="text-terra3 text-sm"
          role="alert"
          data-testid="ai-error"
        >
          {isApiError(askAI.error)
            ? (askAI.error.error?.message ?? t("errorFallback"))
            : t("requestError")}
        </p>
      )}
      <Button
        type="submit"
        disabled={askAI.isPending || question.trim().length === 0}
        data-testid="ai-submit"
      >
        {askAI.isPending ? t("submitPending") : t("submitLabel")}
      </Button>
    </form>
  );
}
