"use client";

import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@country-decision-atlas/ui";
import { useExplainNumberMutation } from "../../entities/ai-assistant/api";
import type { AIExplainNumberResponse } from "../../shared/api/ai";
import { isApiError } from "../../shared/api";
import type { SupportedLocale } from "../../shared/lib/locale";
import { AICitationsList } from "./AICitationsList";
import { AIDisclaimer } from "./AIDisclaimer";
import { AIRefusalState } from "./AIRefusalState";

type AIExplainNumberButtonProps = {
  numberType:
    | "cii_score"
    | "decision_score"
    | "trust_score"
    | "country_drift"
    | "legal_velocity_index"
    | "scenario_specific_risk_score"
    | "contradiction_score"
    | "platform_metric";
  countrySlug: string;
  scenarioSlug?: string;
  value?: number;
  metricKey?: string;
  locale: SupportedLocale;
};

function ExplainContent({ response }: { response: AIExplainNumberResponse }) {
  return (
    <div
      className="flex flex-col gap-3"
      data-testid="ai-explain-number-panel"
    >
      {response.refused ? (
        <AIRefusalState message={response.explanation} />
      ) : (
        <div className="flex flex-col gap-2">
          <p className="text-c1 text-sm leading-relaxed">
            {response.explanation}
          </p>
          <p className="text-c3 text-sm leading-relaxed">
            {response.what_it_means}
          </p>
          <p className="text-c4 text-xs leading-relaxed">
            {response.what_it_does_not_mean}
          </p>
        </div>
      )}
      <AICitationsList citations={response.citations} />
      <AIDisclaimer text={response.disclaimer} />
    </div>
  );
}

export function AIExplainNumberButton({
  numberType,
  countrySlug,
  scenarioSlug,
  value,
  metricKey,
  locale,
}: AIExplainNumberButtonProps) {
  const explainNumber = useExplainNumberMutation();

  function handleOpenChange(open: boolean) {
    if (!open || explainNumber.data || explainNumber.isPending) return;
    explainNumber.mutate({
      number_type: numberType,
      country_slug: countrySlug,
      scenario_slug: scenarioSlug,
      value,
      metric_key: metricKey,
      locale,
    });
  }

  return (
    <div data-testid="ai-explain-number">
      <Popover onOpenChange={handleOpenChange}>
        <PopoverTrigger asChild>
          <button
            type="button"
            aria-label="Объяснить число"
            data-testid="ai-explain-number-button"
            className="border-warm text-c3 hover:border-gold hover:text-gold3 flex h-6 w-6 shrink-0 items-center justify-center rounded-full border font-mono text-xs transition-colors duration-200"
          >
            ?
          </button>
        </PopoverTrigger>
        <PopoverContent className="max-h-96 w-80 overflow-y-auto">
          {explainNumber.isPending && (
            <p className="text-c3 text-sm">Объясняем…</p>
          )}
          {explainNumber.isError && (
            <p
              className="text-terra3 text-sm"
              role="alert"
            >
              {isApiError(explainNumber.error)
                ? (explainNumber.error.error?.message ??
                  "Объяснение временно недоступно.")
                : "Объяснение временно недоступно."}
            </p>
          )}
          {explainNumber.data && (
            <ExplainContent response={explainNumber.data} />
          )}
        </PopoverContent>
      </Popover>
    </div>
  );
}
