"use client";

import { useState } from "react";
import { Button } from "@country-decision-atlas/ui";

import type { DecisionRunRequest } from "../../shared/api/decision";
import { useCreateDecisionPassportMutation } from "../../entities/decision-passports/api";
import { isApiError } from "../../shared/api/http";
import { toApiLocale, type SupportedLocale } from "../../shared/lib/locale";

type DecisionPassportActionsProps = {
  decisionRequest: DecisionRunRequest;
  locale: SupportedLocale;
};

function buildFullUrl(path: string, locale: SupportedLocale): string {
  const origin = typeof window !== "undefined" ? window.location.origin : "";
  return `${origin}/${locale}${path}`;
}

export function DecisionPassportActions({
  decisionRequest,
  locale,
}: DecisionPassportActionsProps) {
  const createPassport = useCreateDecisionPassportMutation();
  const [copied, setCopied] = useState(false);

  async function handleCreate() {
    setCopied(false);
    createPassport.mutate({
      decision_request: decisionRequest,
      locale: toApiLocale(locale),
    });
  }

  const passport = createPassport.data;
  const fullUrl = passport ? buildFullUrl(passport.path, locale) : null;
  const error =
    createPassport.isError && isApiError(createPassport.error)
      ? createPassport.error.error.message
      : createPassport.isError
        ? "Не удалось создать Decision Passport. Попробуйте ещё раз."
        : null;

  async function handleCopy() {
    if (!fullUrl) return;
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(fullUrl);
      } else {
        const textarea = document.createElement("textarea");
        textarea.value = fullUrl;
        textarea.style.position = "fixed";
        textarea.style.opacity = "0";
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand("copy");
        document.body.removeChild(textarea);
      }
      setCopied(true);
    } catch {
      setCopied(false);
    }
  }

  return (
    <div data-testid="decision-passport-actions">
      <Button
        onClick={handleCreate}
        disabled={createPassport.isPending}
        aria-busy={createPassport.isPending}
        aria-label="Создать Decision Passport"
        data-testid="create-passport-button"
      >
        {createPassport.isPending
          ? "Создаём Decision Passport…"
          : "Создать Decision Passport"}
      </Button>

      {error && (
        <p
          role="alert"
          className="text-terra3 mt-2 text-sm"
          data-testid="passport-error"
        >
          {error}
        </p>
      )}

      {passport && fullUrl && (
        <div
          className="mt-4 flex flex-col gap-2"
          data-testid="passport-link-block"
        >
          <a
            href={fullUrl}
            data-testid="passport-link"
            aria-label="Открыть Decision Passport"
            className="text-gold3 hover:text-gold text-sm transition-colors duration-300"
          >
            {fullUrl}
          </a>
          <Button
            variant="ghost"
            onClick={handleCopy}
            aria-label="Скопировать ссылку на Decision Passport"
            data-testid="copy-passport-link"
          >
            {copied ? "Скопировано" : "Скопировать ссылку"}
          </Button>
          <p className="text-c4 text-xs">
            Decision Passport — это сохранённый снимок результата, а не
            консультация.
          </p>
        </div>
      )}
    </div>
  );
}
