"use client";

import { useState } from "react";

import type { CountryListResponse } from "../../shared/api/countries";
import type {
  DecisionWizardAnswers,
  DecisionWizardRecommendation,
} from "../../shared/api/decision";
import { decisionApi } from "../../shared/api";
import { trackEvent } from "../../shared/analytics/client";
import type { SupportedLocale } from "../../shared/lib/locale";
import {
  DECISION_CRITERIA_ORDER,
  type DecisionCriterion,
} from "../decision-personalization";
import { DecisionWizardStep } from "./DecisionWizardStep";
import { DecisionWizardSummary } from "./DecisionWizardSummary";
import { DECISION_WIZARD_LABELS } from "./decision-wizard-labels";

type DecisionWizardApplyPayload = {
  scenarioSlug: string;
  personaSlug: string;
  candidateCountrySlugs: string[];
  customWeights: Record<DecisionCriterion, number>;
};

type DecisionWizardPanelProps = {
  locale: SupportedLocale;
  countries: CountryListResponse;
  originCountrySlug: string;
  onApply: (payload: DecisionWizardApplyPayload) => void;
};

function normalizeWeights(
  recommendation: DecisionWizardRecommendation,
): Record<DecisionCriterion, number> {
  const weights = { ...recommendation.initial_custom_weights };
  return DECISION_CRITERIA_ORDER.reduce(
    (acc, criterion) => {
      acc[criterion] = Number(weights[criterion] ?? 0);
      return acc;
    },
    {} as Record<DecisionCriterion, number>,
  );
}

export function DecisionWizardPanel({
  locale,
  countries,
  originCountrySlug,
  onApply,
}: DecisionWizardPanelProps) {
  const labels = DECISION_WIZARD_LABELS[locale];
  const [isOpen, setIsOpen] = useState(false);
  const [hasTrackedOpen, setHasTrackedOpen] = useState(false);
  const [answers, setAnswers] = useState<DecisionWizardAnswers>({
    primary_goal: "residence",
    origin_country_slug: originCountrySlug,
    budget_level: "unknown",
    family_status: "unknown",
    work_priority: "medium",
    safety_priority: "medium",
    citizenship_priority: "medium",
    business_priority: "medium",
    timeframe: "unknown",
  });
  const [isResolving, setIsResolving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [recommendation, setRecommendation] =
    useState<DecisionWizardRecommendation | null>(null);

  function updateAnswer<Key extends keyof DecisionWizardAnswers>(
    key: Key,
    value: DecisionWizardAnswers[Key],
  ) {
    setAnswers((prev) => ({ ...prev, [key]: value }));
  }

  function toggleOpen() {
    const nextOpen = !isOpen;
    setIsOpen(nextOpen);
    if (nextOpen && !hasTrackedOpen) {
      setHasTrackedOpen(true);
      void trackEvent({
        event_type: "decision_wizard_started",
        source: "web",
        path: "/decision",
        locale,
      });
    }
  }

  async function handleResolve() {
    setIsResolving(true);
    setError(null);
    setRecommendation(null);
    try {
      const res = await decisionApi.resolveWizard({
        ...answers,
        origin_country_slug: originCountrySlug,
      });
      const availableCountrySlugs = new Set(
        countries.items.map((country) => country.slug),
      );
      const candidates = res.candidate_country_slugs.filter((slug) =>
        availableCountrySlugs.has(slug),
      );
      onApply({
        scenarioSlug: res.recommended_scenario_slug,
        personaSlug: res.recommended_persona_slug ?? "",
        candidateCountrySlugs: candidates.length > 0 ? candidates : [originCountrySlug],
        customWeights: normalizeWeights(res),
      });
      setRecommendation(res);
    } catch {
      setError(labels.unavailable);
    } finally {
      setIsResolving(false);
    }
  }

  return (
    <section className="decisionWizard" data-testid="decision-wizard">
      <div className="decisionWizardHeader">
        <div>
          <h2 className="decisionWizardTitle">{labels.title}</h2>
          <p className="formHint">{labels.hint}</p>
        </div>
        <button
          type="button"
          className="decisionWizardToggle"
          aria-expanded={isOpen}
          onClick={toggleOpen}
          data-testid="decision-wizard-toggle"
        >
          {isOpen ? labels.close : labels.open}
        </button>
      </div>

      {isOpen && (
        <div className="decisionWizardPanel" data-testid="decision-wizard-panel">
          <div className="decisionWizardGrid">
            <DecisionWizardStep
              label={labels.goal}
              value={answers.primary_goal}
              options={labels.primaryGoalOptions}
              onChange={(value) => updateAnswer("primary_goal", value)}
              testId="decision-wizard-primary-goal"
            />
            <DecisionWizardStep
              label={labels.budget}
              value={answers.budget_level}
              options={labels.budgetOptions}
              onChange={(value) => updateAnswer("budget_level", value)}
              testId="decision-wizard-budget"
            />
            <DecisionWizardStep
              label={labels.family}
              value={answers.family_status}
              options={labels.familyOptions}
              onChange={(value) => updateAnswer("family_status", value)}
              testId="decision-wizard-family"
            />
            <DecisionWizardStep
              label={labels.timeframe}
              value={answers.timeframe}
              options={labels.timeframeOptions}
              onChange={(value) => updateAnswer("timeframe", value)}
              testId="decision-wizard-timeframe"
            />
          </div>

          <div className="decisionWizardGrid decisionWizardPriorityGrid">
            <DecisionWizardStep
              label={labels.workPriority}
              value={answers.work_priority}
              options={labels.levelOptions}
              onChange={(value) => updateAnswer("work_priority", value)}
              testId="decision-wizard-work_priority"
            />
            <DecisionWizardStep
              label={labels.safetyPriority}
              value={answers.safety_priority}
              options={labels.levelOptions}
              onChange={(value) => updateAnswer("safety_priority", value)}
              testId="decision-wizard-safety_priority"
            />
            <DecisionWizardStep
              label={labels.citizenshipPriority}
              value={answers.citizenship_priority}
              options={labels.levelOptions}
              onChange={(value) => updateAnswer("citizenship_priority", value)}
              testId="decision-wizard-citizenship_priority"
            />
            <DecisionWizardStep
              label={labels.businessPriority}
              value={answers.business_priority}
              options={labels.levelOptions}
              onChange={(value) => updateAnswer("business_priority", value)}
              testId="decision-wizard-business_priority"
            />
          </div>

          <button
            type="button"
            className="runButton"
            onClick={handleResolve}
            disabled={isResolving}
            aria-busy={isResolving}
            data-testid="decision-wizard-apply"
          >
            {isResolving ? labels.applying : labels.apply}
          </button>

          {error && (
            <p className="formError" role="alert" data-testid="decision-wizard-error">
              {error}
            </p>
          )}
          {recommendation && (
            <DecisionWizardSummary recommendation={recommendation} labels={labels} />
          )}
        </div>
      )}
    </section>
  );
}
