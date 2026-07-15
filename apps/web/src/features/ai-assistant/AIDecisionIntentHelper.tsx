"use client";

import { useState } from "react";
import { Badge, Button, Field, FieldLabel } from "@country-decision-atlas/ui";
import { useParseDecisionIntentMutation } from "../../entities/ai-assistant/api";
import type { AIDecisionIntentResponse } from "../../shared/api/ai";
import { isApiError } from "../../shared/api";
import type { SupportedLocale } from "../../shared/lib/locale";

const inputClass =
  "border-warm bg-bg2 text-c1 font-body border px-4 py-2.5 text-sm outline-none focus-visible:border-gold transition-colors duration-200";

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
  const parseDecisionIntent = useParseDecisionIntentMutation();

  async function handleSubmit() {
    parseDecisionIntent.mutate({ text, locale });
  }

  return (
    <div
      className="border-warm flex flex-col gap-3 border px-4 py-4"
      data-testid="ai-decision-helper"
    >
      <Field>
        <FieldLabel htmlFor="ai-decision-intent">
          Опишите вашу ситуацию
        </FieldLabel>
        <textarea
          id="ai-decision-intent"
          className={inputClass}
          value={text}
          onChange={(event) => setText(event.target.value)}
          rows={4}
          data-testid="ai-decision-intent-input"
        />
      </Field>
      <Button
        type="button"
        onClick={() => void handleSubmit()}
        disabled={parseDecisionIntent.isPending || text.trim().length === 0}
        data-testid="ai-decision-intent-submit"
      >
        {parseDecisionIntent.isPending
          ? "Подбираем…"
          : "Подобрать scenario/persona"}
      </Button>
      {parseDecisionIntent.isError && (
        <p
          className="text-terra3 text-sm"
          role="alert"
          data-testid="ai-decision-error"
        >
          {isApiError(parseDecisionIntent.error)
            ? (parseDecisionIntent.error.error?.message ??
              "AI-подсказка временно недоступна.")
            : "Ошибка запроса."}
        </p>
      )}
      {parseDecisionIntent.data && (
        <div
          className="bg-bg2 flex flex-col gap-2 p-3 text-sm"
          data-testid="ai-decision-result"
        >
          {parseDecisionIntent.data.refused ? (
            <p className="text-c3">
              {parseDecisionIntent.data.refusal?.reason ??
                "Недостаточно данных."}
            </p>
          ) : (
            <>
              <div className="flex flex-wrap items-center gap-2">
                <Badge variant="default">
                  Scenario: {parseDecisionIntent.data.scenario_slug}
                </Badge>
                <Badge variant="default">
                  Persona: {parseDecisionIntent.data.persona_slug}
                </Badge>
              </div>
              <p className="text-c3">
                Кандидаты:{" "}
                {(parseDecisionIntent.data.candidate_country_slugs ?? []).join(
                  ", ",
                )}
              </p>
              <Button
                type="button"
                variant="ghost"
                onClick={() => onApply(parseDecisionIntent.data!)}
                data-testid="ai-decision-apply"
              >
                Применить подсказки
              </Button>
            </>
          )}
          <p className="text-c4 text-xs">
            {parseDecisionIntent.data.disclaimer}
          </p>
        </div>
      )}
    </div>
  );
}
