"use client";

import { useState } from "react";
import { Button, Card, Kicker } from "@country-decision-atlas/ui";

import type { CountryListResponse } from "../../shared/api/countries";
import type {
  DecisionWizardAnswers,
  DecisionWizardRecommendation,
} from "../../shared/api/decision";
import { useResolveWizardMutation } from "../../entities/decision/api";
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
  const effectiveOriginSlug =
    originCountrySlug || countries.items[0]?.slug || "";
  const [isOpen, setIsOpen] = useState(false);
  const [hasTrackedOpen, setHasTrackedOpen] = useState(false);
  const [answers, setAnswers] = useState<DecisionWizardAnswers>({
    primary_goal: "residence",
    origin_country_slug: effectiveOriginSlug,
    budget_level: "unknown",
    family_status: "unknown",
    work_priority: "medium",
    safety_priority: "medium",
    citizenship_priority: "medium",
    business_priority: "medium",
    timeframe: "unknown",
  });
  const [recommendation, setRecommendation] =
    useState<DecisionWizardRecommendation | null>(null);
  const resolveWizard = useResolveWizardMutation();

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
    setRecommendation(null);
    try {
      const res = await resolveWizard.mutateAsync({
        ...answers,
        origin_country_slug: effectiveOriginSlug,
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
        candidateCountrySlugs:
          candidates.length > 0 ? candidates : [effectiveOriginSlug],
        customWeights: normalizeWeights(res),
      });
      setRecommendation(res);
    } catch {
      // handled via resolveWizard.isError below
    }
  }

  return (
    <div data-testid="decision-wizard">
    <Card
      interactive={false}
      className="flex flex-col gap-4"
    >
      <div className="flex items-center justify-between gap-4">
        <div className="flex flex-col gap-1">
          <Kicker>{labels.title}</Kicker>
          <p className="text-c3 text-sm">{labels.hint}</p>
        </div>
        <Button
          variant="ghost"
          aria-expanded={isOpen}
          onClick={toggleOpen}
          data-testid="decision-wizard-toggle"
        >
          {isOpen ? labels.close : labels.open}
        </Button>
      </div>

      {isOpen && (
        <div
          className="flex flex-col gap-6"
          data-testid="decision-wizard-panel"
        >
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
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

          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
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

          <Button
            onClick={handleResolve}
            disabled={resolveWizard.isPending}
            aria-busy={resolveWizard.isPending}
            data-testid="decision-wizard-apply"
          >
            {resolveWizard.isPending ? labels.applying : labels.apply}
          </Button>

          {resolveWizard.isError && (
            <p
              role="alert"
              className="text-terra3 text-sm"
              data-testid="decision-wizard-error"
            >
              {labels.unavailable}
            </p>
          )}
          {recommendation && (
            <DecisionWizardSummary
              recommendation={recommendation}
              labels={labels}
            />
          )}
        </div>
      )}
    </Card>
    </div>
  );
}
