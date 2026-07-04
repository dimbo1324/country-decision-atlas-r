"use client";

import { FormEvent, useState } from "react";
import type { AIAskResponse } from "../../shared/api/ai";
import { aiApi, isApiError } from "../../shared/api";
import type { SupportedLocale } from "../../shared/lib/locale";

type AIAskFormProps = {
  locale: SupportedLocale;
  onResponse: (response: AIAskResponse) => void;
};

export function AIAskForm({ locale, onResponse }: AIAskFormProps) {
  const [question, setQuestion] = useState(
    "Что известно об Уругвае для переезда?",
  );
  const [countrySlug, setCountrySlug] = useState("uruguay");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      const response = await aiApi.askAI({
        question,
        locale,
        country_slug: countrySlug || undefined,
      });
      onResponse(response);
    } catch (err: unknown) {
      if (isApiError(err)) {
        setError(err.error?.message ?? "AI-помощник временно недоступен.");
      } else {
        setError(err instanceof Error ? err.message : "Ошибка запроса.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form
      className="decisionForm"
      onSubmit={handleSubmit}
      data-testid="ai-ask-form"
    >
      <div className="formGroup">
        <label
          className="formLabel"
          htmlFor="ai-question"
        >
          Вопрос
        </label>
        <textarea
          id="ai-question"
          className="formTextarea"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          data-testid="ai-question-input"
          rows={4}
        />
      </div>
      <div className="formGroup">
        <label
          className="formLabel"
          htmlFor="ai-country"
        >
          Страна, если нужно
        </label>
        <input
          id="ai-country"
          className="formInput"
          value={countrySlug}
          onChange={(event) => setCountrySlug(event.target.value)}
          data-testid="ai-country-input"
        />
      </div>
      {error && (
        <p
          className="formError"
          role="alert"
          data-testid="ai-error"
        >
          {error}
        </p>
      )}
      <button
        className="runButton"
        type="submit"
        disabled={isSubmitting || question.trim().length === 0}
        data-testid="ai-submit"
      >
        {isSubmitting ? "Готовим ответ…" : "Спросить"}
      </button>
    </form>
  );
}
