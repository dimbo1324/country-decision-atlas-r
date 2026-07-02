"use client";

import { useState } from "react";
import type { AIDecisionIntentResponse } from "../../shared/api/ai";
import { aiApi, isApiError } from "../../shared/api";
import type { SupportedLocale } from "../../shared/lib/locale";

type AIDecisionIntentHelperProps = {
  locale: SupportedLocale;
  onApply: (payload: AIDecisionIntentResponse) => void;
};

export function AIDecisionIntentHelper({
  locale,
  onApply,
}: AIDecisionIntentHelperProps) {
  const [text, setText] = useState(
    "Я хочу переехать с семьёй, бюджет ограничен, важна безопасность и путь к гражданству.",
  );
  const [response, setResponse] = useState<AIDecisionIntentResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit() {
    setError(null);
    setIsLoading(true);
    try {
      const result = await aiApi.parseDecisionIntent({ text, locale });
      setResponse(result);
    } catch (err: unknown) {
      if (isApiError(err)) {
        setError(err.error?.message ?? "AI-подсказка временно недоступна.");
      } else {
        setError(err instanceof Error ? err.message : "Ошибка запроса.");
      }
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="formGroup" data-testid="ai-decision-helper">
      <label className="formLabel" htmlFor="ai-decision-intent">
        Опишите вашу ситуацию
      </label>
      <textarea
        id="ai-decision-intent"
        className="formTextarea"
        value={text}
        onChange={(event) => setText(event.target.value)}
        rows={4}
        data-testid="ai-decision-intent-input"
      />
      <button
        type="button"
        className="runButton"
        onClick={handleSubmit}
        disabled={isLoading || text.trim().length === 0}
        data-testid="ai-decision-intent-submit"
      >
        {isLoading ? "Подбираем…" : "Подобрать scenario/persona"}
      </button>
      {error && (
        <p className="formError" role="alert" data-testid="ai-decision-error">
          {error}
        </p>
      )}
      {response && (
        <div className="notice" data-testid="ai-decision-result">
          {response.refused ? (
            <p>{response.refusal?.reason ?? "Недостаточно данных."}</p>
          ) : (
            <>
              <p>
                Scenario: <strong>{response.scenario_slug}</strong> · Persona:{" "}
                <strong>{response.persona_slug}</strong>
              </p>
              <p>Кандидаты: {(response.candidate_country_slugs ?? []).join(", ")}</p>
              <button
                type="button"
                className="internalLink"
                onClick={() => onApply(response)}
                data-testid="ai-decision-apply"
              >
                Применить подсказки
              </button>
            </>
          )}
          <p className="formHint">{response.disclaimer}</p>
        </div>
      )}
    </div>
  );
}
