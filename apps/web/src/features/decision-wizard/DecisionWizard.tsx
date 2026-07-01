"use client";

import { useState } from "react";

import type { CountryListResponse } from "../../shared/api/countries";
import type {
  DecisionWizardAnswers,
  DecisionWizardRecommendation,
} from "../../shared/api/decision";
import { decisionApi } from "../../shared/api";
import type { SupportedLocale } from "../../shared/lib/locale";
import {
  DECISION_CRITERIA_ORDER,
  type DecisionCriterion,
} from "../decision-personalization";

type DecisionWizardApplyPayload = {
  scenarioSlug: string;
  personaSlug: string;
  candidateCountrySlugs: string[];
  customWeights: Record<DecisionCriterion, number>;
};

type DecisionWizardProps = {
  locale: SupportedLocale;
  countries: CountryListResponse;
  originCountrySlug: string;
  onApply: (payload: DecisionWizardApplyPayload) => void;
};

const PRIMARY_GOAL_OPTIONS: Array<{
  value: DecisionWizardAnswers["primary_goal"];
  label: string;
}> = [
  { value: "residence", label: "Р’РќР– Рё РїРµСЂРµРµР·Рґ" },
  { value: "citizenship", label: "РџРњР– Рё РіСЂР°Р¶РґР°РЅСЃС‚РІРѕ" },
  { value: "low_budget", label: "РќРёР·РєРёР№ Р±СЋРґР¶РµС‚" },
  { value: "business", label: "Р‘РёР·РЅРµСЃ" },
  { value: "safety", label: "Р‘РµР·РѕРїР°СЃРЅРѕСЃС‚СЊ" },
  { value: "remote_work", label: "РЈРґР°Р»С‘РЅРЅР°СЏ СЂР°Р±РѕС‚Р°" },
  { value: "study", label: "РЈС‡С‘Р±Р°" },
];

const LEVEL_OPTIONS = [
  { value: "low", label: "РќРёР·РєРёР№" },
  { value: "medium", label: "РЎСЂРµРґРЅРёР№" },
  { value: "high", label: "Р’С‹СЃРѕРєРёР№" },
] as const;

const BUDGET_OPTIONS: Array<{
  value: DecisionWizardAnswers["budget_level"];
  label: string;
}> = [{ value: "unknown", label: "РќРµ Р·РЅР°СЋ" }, ...LEVEL_OPTIONS];

const FAMILY_OPTIONS: Array<{
  value: DecisionWizardAnswers["family_status"];
  label: string;
}> = [
  { value: "unknown", label: "РќРµ РІР°Р¶РЅРѕ" },
  { value: "solo", label: "РћРґРёРЅ" },
  { value: "couple", label: "РџР°СЂР°" },
  { value: "family_with_children", label: "РЎРµРјСЊСЏ СЃ РґРµС‚СЊРјРё" },
];

const TIMEFRAME_OPTIONS: Array<{
  value: DecisionWizardAnswers["timeframe"];
  label: string;
}> = [
  { value: "unknown", label: "РќРµ РІР°Р¶РЅРѕ" },
  { value: "fast", label: "Р‘С‹СЃС‚СЂРѕ" },
  { value: "medium", label: "РЎСЂРµРґРЅРµСЃСЂРѕС‡РЅРѕ" },
  { value: "long", label: "Р”РѕР»РіРѕСЃСЂРѕС‡РЅРѕ" },
];

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

export function DecisionWizard({
  locale,
  countries,
  originCountrySlug,
  onApply,
}: DecisionWizardProps) {
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
      setError(
        locale === "ru"
          ? "РњР°СЃС‚РµСЂ РІСЂРµРјРµРЅРЅРѕ РЅРµРґРѕСЃС‚СѓРїРµРЅ. РњРѕР¶РЅРѕ РїСЂРѕРґРѕР»Р¶РёС‚СЊ СЂСѓС‡РЅСѓСЋ."
          : "Wizard is temporarily unavailable. You can continue manually.",
      );
    } finally {
      setIsResolving(false);
    }
  }

  return (
    <section className="decisionWizard" data-testid="decision-wizard">
      <div className="decisionWizardHeader">
        <div>
          <h2 className="decisionWizardTitle">РњР°СЃС‚РµСЂ РїРѕРґР±РѕСЂР°</h2>
          <p className="formHint">
            РћС‚РІРµС‚СЊС‚Рµ РЅР° РЅРµСЃРєРѕР»СЊРєРѕ РІРѕРїСЂРѕСЃРѕРІ, Рё С„РѕСЂРјР°
            Р·Р°РїРѕР»РЅРёС‚СЃСЏ Р±РµР· СЃРѕС…СЂР°РЅРµРЅРёСЏ РїСЂРѕС„РёР»СЏ.
          </p>
        </div>
        {recommendation && (
          <span className="badge" data-testid="decision-wizard-confidence">
            {recommendation.confidence}
          </span>
        )}
      </div>

      <div className="decisionWizardGrid">
        <label className="formGroup">
          <span className="formLabel">Р¦РµР»СЊ</span>
          <select
            className="formSelect"
            value={answers.primary_goal}
            onChange={(event) =>
              setAnswers((prev) => ({
                ...prev,
                primary_goal: event.target
                  .value as DecisionWizardAnswers["primary_goal"],
              }))
            }
            data-testid="decision-wizard-primary-goal"
          >
            {PRIMARY_GOAL_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>

        <label className="formGroup">
          <span className="formLabel">Р‘СЋРґР¶РµС‚</span>
          <select
            className="formSelect"
            value={answers.budget_level}
            onChange={(event) =>
              setAnswers((prev) => ({
                ...prev,
                budget_level: event.target
                  .value as DecisionWizardAnswers["budget_level"],
              }))
            }
            data-testid="decision-wizard-budget"
          >
            {BUDGET_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>

        <label className="formGroup">
          <span className="formLabel">РЎРµРјСЊСЏ</span>
          <select
            className="formSelect"
            value={answers.family_status}
            onChange={(event) =>
              setAnswers((prev) => ({
                ...prev,
                family_status: event.target
                  .value as DecisionWizardAnswers["family_status"],
              }))
            }
            data-testid="decision-wizard-family"
          >
            {FAMILY_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>

        <label className="formGroup">
          <span className="formLabel">РЎСЂРѕРє</span>
          <select
            className="formSelect"
            value={answers.timeframe}
            onChange={(event) =>
              setAnswers((prev) => ({
                ...prev,
                timeframe: event.target.value as DecisionWizardAnswers["timeframe"],
              }))
            }
            data-testid="decision-wizard-timeframe"
          >
            {TIMEFRAME_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="decisionWizardGrid decisionWizardPriorityGrid">
        {(
          [
            ["work_priority", "Р Р°Р±РѕС‚Р°"],
            ["safety_priority", "Р‘РµР·РѕРїР°СЃРЅРѕСЃС‚СЊ"],
            ["citizenship_priority", "РЎС‚Р°С‚СѓСЃ"],
            ["business_priority", "Р‘РёР·РЅРµСЃ"],
          ] as const
        ).map(([key, label]) => (
          <label key={key} className="formGroup">
            <span className="formLabel">{label}</span>
            <select
              className="formSelect"
              value={answers[key]}
              onChange={(event) =>
                setAnswers((prev) => ({
                  ...prev,
                  [key]: event.target.value as DecisionWizardAnswers[typeof key],
                }))
              }
              data-testid={`decision-wizard-${key}`}
            >
              {LEVEL_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
        ))}
      </div>

      <button
        type="button"
        className="runButton"
        onClick={handleResolve}
        disabled={isResolving}
        aria-busy={isResolving}
        data-testid="decision-wizard-apply"
      >
        {isResolving ? "РџРѕРґР±РёСЂР°РµРјвЂ¦" : "Р—Р°РїРѕР»РЅРёС‚СЊ С„РѕСЂРјСѓ"}
      </button>

      {error && (
        <p className="formError" role="alert" data-testid="decision-wizard-error">
          {error}
        </p>
      )}
      {recommendation && (
        <div className="decisionWizardResult" data-testid="decision-wizard-result">
          <strong>{recommendation.recommended_scenario_slug}</strong>
          {recommendation.recommended_persona_slug && (
            <span>{recommendation.recommended_persona_slug}</span>
          )}
        </div>
      )}
    </section>
  );
}
