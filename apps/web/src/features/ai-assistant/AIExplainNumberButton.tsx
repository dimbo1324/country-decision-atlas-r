"use client";

import { useState } from "react";
import type { AIExplainNumberResponse } from "../../shared/api/ai";
import { aiApi, isApiError } from "../../shared/api";
import type { SupportedLocale } from "../../shared/lib/locale";
import { AICitationsList } from "./AICitationsList";
import { AIDisclaimer } from "./AIDisclaimer";
import { AIRefusalState } from "./AIRefusalState";

type AIExplainNumberButtonProps = {
  numberType: "cii_score" | "trust_score" | "country_drift" | "platform_metric";
  countrySlug: string;
  value?: number;
  metricKey?: string;
  locale: SupportedLocale;
};

export function AIExplainNumberButton({
  numberType,
  countrySlug,
  value,
  metricKey,
  locale,
}: AIExplainNumberButtonProps) {
  const [response, setResponse] = useState<AIExplainNumberResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function handleClick() {
    setError(null);
    setIsLoading(true);
    try {
      const result = await aiApi.explainNumber({
        number_type: numberType,
        country_slug: countrySlug,
        value,
        metric_key: metricKey,
        locale,
      });
      setResponse(result);
    } catch (err: unknown) {
      if (isApiError(err)) {
        setError(err.error?.message ?? "Объяснение временно недоступно.");
      } else {
        setError(err instanceof Error ? err.message : "Ошибка запроса.");
      }
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div data-testid="ai-explain-number">
      <button
        type="button"
        className="internalLink"
        onClick={handleClick}
        disabled={isLoading}
        data-testid="ai-explain-number-button"
      >
        {isLoading ? "Объясняем…" : "Объяснить число"}
      </button>
      {error && (
        <p className="formError" role="alert">
          {error}
        </p>
      )}
      {response && (
        <div className="notice" data-testid="ai-explain-number-panel">
          {response.refused ? (
            <AIRefusalState message={response.explanation} />
          ) : (
            <>
              <p>{response.explanation}</p>
              <p>{response.what_it_means}</p>
              <p className="formHint">{response.what_it_does_not_mean}</p>
            </>
          )}
          <AICitationsList citations={response.citations} />
          <AIDisclaimer text={response.disclaimer} />
        </div>
      )}
    </div>
  );
}
