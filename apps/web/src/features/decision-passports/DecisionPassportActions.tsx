"use client";

import { useState } from "react";

import type { DecisionRunRequest } from "../../shared/api/decision";
import type { DecisionPassportCreateResponse } from "../../shared/api/decision-passports";
import { decisionPassportsApi } from "../../shared/api";
import { isApiError } from "../../shared/api/http";
import type { SupportedLocale } from "../../shared/lib/locale";

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
  const [isCreating, setIsCreating] = useState(false);
  const [passport, setPassport] =
    useState<DecisionPassportCreateResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  async function handleCreate() {
    setIsCreating(true);
    setError(null);
    setCopied(false);
    try {
      const response = await decisionPassportsApi.createDecisionPassport({
        decision_request: decisionRequest,
        locale,
      });
      setPassport(response);
    } catch (err: unknown) {
      setError(
        isApiError(err)
          ? err.error.message
          : "Не удалось создать Decision Passport. Попробуйте ещё раз.",
      );
    } finally {
      setIsCreating(false);
    }
  }

  const fullUrl = passport ? buildFullUrl(passport.path, locale) : null;

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
    <div
      className="decisionPassportActions"
      data-testid="decision-passport-actions"
    >
      <button
        type="button"
        className="runButton"
        onClick={handleCreate}
        disabled={isCreating}
        aria-busy={isCreating}
        aria-label="Создать Decision Passport"
        data-testid="create-passport-button"
      >
        {isCreating
          ? "Создаём Decision Passport…"
          : "Создать Decision Passport"}
      </button>

      {error && (
        <p
          className="formError"
          role="alert"
          data-testid="passport-error"
        >
          {error}
        </p>
      )}

      {passport && fullUrl && (
        <div
          className="passportLinkBlock"
          data-testid="passport-link-block"
        >
          <a
            href={fullUrl}
            data-testid="passport-link"
            aria-label="Открыть Decision Passport"
          >
            {fullUrl}
          </a>
          <button
            type="button"
            onClick={handleCopy}
            aria-label="Скопировать ссылку на Decision Passport"
            data-testid="copy-passport-link"
          >
            {copied ? "Скопировано" : "Скопировать ссылку"}
          </button>
          <p className="formHint">
            Decision Passport — это сохранённый снимок результата, а не
            консультация.
          </p>
        </div>
      )}
    </div>
  );
}
