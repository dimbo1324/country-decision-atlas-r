"use client";

import { Suspense, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  AnalysisOverlay,
  Button,
  Card,
  Field,
  FieldLabel,
} from "@country-decision-atlas/ui";
import { useAppLocale } from "../../shared/lib/useAppLocale";

import type {
  DecisionRunRequest,
  DecisionRunResponse,
} from "../../shared/api/decision";
import {
  allCountriesQuery,
  scenariosQuery,
  personasQuery,
  useRunDecisionMutation,
} from "../../entities/decision/api";
import { useAnalyticsEvent } from "../../shared/analytics/useAnalyticsEvent";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";
import { DecisionPassportActions } from "../decision-passports";
import { DecisionResults } from "./DecisionResults";
import {
  DEFAULT_DECISION_READY_SCENARIO_SLUG,
  isDecisionReadyScenario,
} from "./decision-ready-scenarios";
import { DecisionCiiComparison } from "../decision-visual-comparison";
import { DecisionRiskContext } from "../platform-intelligence";
import {
  DECISION_CRITERIA_ORDER,
  DEFAULT_DECISION_WEIGHTS,
  DecisionWeightSliders,
  type DecisionCriterion,
} from "../decision-personalization";
import { DecisionWizard } from "../decision-wizard";
import { AIDecisionIntentHelper } from "../ai-assistant";
import type { AIDecisionIntentResponse } from "../../shared/api/ai";

type RunError = { error?: { code?: string; message?: string } } | string | null;

const DECISION_PERSONALIZATION_ERROR_MESSAGES: Record<string, string> = {
  unknown_custom_weight_criterion: "Проверьте значения приоритетов.",
  custom_weights_incomplete: "Проверьте значения приоритетов.",
  custom_weight_out_of_range: "Проверьте значения приоритетов.",
  custom_weight_invalid: "Проверьте значения приоритетов.",
  custom_weights_sum_zero: "Сумма приоритетов должна быть больше нуля.",
  decision_personalization_disabled:
    "Настройка приоритетов временно недоступна.",
};

function DecisionFormInner() {
  const locale = useAppLocale();
  const trackAnalyticsEvent = useAnalyticsEvent();

  const { data: countries, isPending: countriesPending } = useQuery(
    allCountriesQuery(locale),
  );
  const { data: scenarios, isPending: scenariosPending } = useQuery(
    scenariosQuery(locale),
  );
  const { data: personas } = useQuery(personasQuery(locale));

  const [originCountrySlug, setOriginCountrySlug] = useState("");
  const [candidateCountrySlugs, setCandidateCountrySlugs] = useState<string[]>([
    "russia",
    "uruguay",
  ]);
  const [scenarioSlug, setScenarioSlug] = useState<string>(
    DEFAULT_DECISION_READY_SCENARIO_SLUG,
  );
  const [selectedPersonaSlug, setSelectedPersonaSlug] = useState("");

  const [customWeights, setCustomWeights] = useState<
    Record<DecisionCriterion, number>
  >({
    ...DEFAULT_DECISION_WEIGHTS,
  });
  const [personalizationTouched, setPersonalizationTouched] = useState(false);

  const [result, setResult] = useState<DecisionRunResponse | null>(null);
  const [lastDecisionRequest, setLastDecisionRequest] =
    useState<DecisionRunRequest | null>(null);
  const [runError, setRunError] = useState<RunError>(null);
  const runDecision = useRunDecisionMutation();

  function toggleCandidate(slug: string) {
    setCandidateCountrySlugs((prev) =>
      prev.includes(slug) ? prev.filter((s) => s !== slug) : [...prev, slug],
    );
  }

  function handleWeightChange(criterion: DecisionCriterion, value: number) {
    setCustomWeights((prev) => ({ ...prev, [criterion]: value }));
    setPersonalizationTouched(true);
  }

  function handleWeightReset() {
    setCustomWeights({ ...DEFAULT_DECISION_WEIGHTS });
    setPersonalizationTouched(false);
  }

  function handleWizardApply(payload: {
    scenarioSlug: string;
    personaSlug: string;
    candidateCountrySlugs: string[];
    customWeights: Record<DecisionCriterion, number>;
  }) {
    setScenarioSlug(payload.scenarioSlug);
    setSelectedPersonaSlug(payload.personaSlug);
    setCandidateCountrySlugs(payload.candidateCountrySlugs);
    setCustomWeights(payload.customWeights);
    setPersonalizationTouched(true);
    setRunError(null);
  }

  function handleAiDecisionApply(payload: AIDecisionIntentResponse) {
    if (
      payload.scenario_slug &&
      isDecisionReadyScenario(payload.scenario_slug)
    ) {
      setScenarioSlug(payload.scenario_slug);
    }
    if (payload.persona_slug) {
      setSelectedPersonaSlug(payload.persona_slug);
    }
    if (payload.origin_country_slug) {
      setOriginCountrySlug(payload.origin_country_slug);
    }
    const candidateHints = payload.candidate_country_slugs ?? [];
    if (candidateHints.length > 0) {
      const knownSlugs = new Set(
        countries?.items.map((country) => country.slug) ?? [],
      );
      const next = candidateHints.filter((slug) => knownSlugs.has(slug));
      if (next.length > 0) {
        setCandidateCountrySlugs(next);
      }
    }
    const nextWeights = { ...customWeights };
    let changed = false;
    const weightHints = payload.weight_hints ?? {};
    for (const criterion of DECISION_CRITERIA_ORDER) {
      const value = weightHints[criterion];
      if (typeof value === "number" && Number.isFinite(value)) {
        nextWeights[criterion] = Math.max(0, Math.min(100, Math.round(value)));
        changed = true;
      }
    }
    if (changed) {
      setCustomWeights(nextWeights);
      setPersonalizationTouched(true);
    }
    setRunError(null);
  }

  const customWeightsSum = DECISION_CRITERIA_ORDER.reduce(
    (total, criterion) => total + customWeights[criterion],
    0,
  );
  const customWeightsBlocked = personalizationTouched && customWeightsSum === 0;

  async function handleRun() {
    if (candidateCountrySlugs.length === 0) return;
    if (customWeightsBlocked) return;
    trackAnalyticsEvent({
      event_type: "decision_started",
      source: "web",
      scenario_slug: scenarioSlug,
      persona_slug: selectedPersonaSlug || undefined,
      metadata: {
        candidate_count: candidateCountrySlugs.length,
      },
    });
    setRunError(null);
    setResult(null);
    const decisionRequest: DecisionRunRequest = {
      candidate_country_slugs: candidateCountrySlugs,
      scenario_slug: scenarioSlug,
      locale,
      ...(originCountrySlug ? { origin_country_slug: originCountrySlug } : {}),
      ...(selectedPersonaSlug ? { persona: selectedPersonaSlug } : {}),
      ...(personalizationTouched ? { custom_weights: customWeights } : {}),
    };
    try {
      const res = await runDecision.mutateAsync(decisionRequest);
      setResult(res);
      setLastDecisionRequest(decisionRequest);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setRunError(err.message);
      } else {
        setRunError(
          typeof err === "object" && err !== null && "error" in err
            ? (err as { error?: { code?: string; message?: string } })
            : "Произошла ошибка при запросе",
        );
      }
    }
  }

  if (countriesPending || scenariosPending) {
    return <LoadingState message="Загрузка стран и сценариев…" />;
  }
  if (!countries || !scenarios) {
    return <ErrorState error="Не удалось загрузить данные" />;
  }

  const decisionReadyScenarios = scenarios.items.filter((s) =>
    isDecisionReadyScenario(s.slug),
  );

  const noScenariosAvailable = decisionReadyScenarios.length === 0;

  const runErrorCode =
    runError !== null && typeof runError === "object"
      ? (runError as { error?: { code?: string } }).error?.code
      : undefined;

  const resolvedRunError =
    runErrorCode === "decision_score_not_found"
      ? "Этот сценарий пока недоступен для выбранных стран. Пожалуйста, выберите один из MVP-сценариев подбора."
      : runErrorCode && runErrorCode in DECISION_PERSONALIZATION_ERROR_MESSAGES
        ? DECISION_PERSONALIZATION_ERROR_MESSAGES[runErrorCode]
        : runError;

  return (
    <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
      <AnalysisOverlay active={runDecision.isPending} />
      <Card
        interactive={false}
        className="flex flex-col gap-6"
      >
        <DecisionWizard
          locale={locale}
          countries={countries}
          originCountrySlug={originCountrySlug}
          onApply={handleWizardApply}
        />

        <AIDecisionIntentHelper
          locale={locale}
          onApply={handleAiDecisionApply}
        />

        <Field>
          <FieldLabel htmlFor="origin-select">Страна отправления</FieldLabel>
          <select
            id="origin-select"
            className="border-warm bg-bg2 text-c2 focus-visible:border-gold w-full border px-3 py-2 text-sm outline-none"
            value={originCountrySlug}
            onChange={(e) => setOriginCountrySlug(e.target.value)}
            data-testid="origin-select"
          >
            <option value="">Не указано</option>
            {countries.items.map((c) => (
              <option
                key={c.slug}
                value={c.slug}
              >
                {c.name}
              </option>
            ))}
          </select>
          <p className="text-c4 text-xs">
            Страна отправления влияет только на контекст, не на базовый рейтинг
          </p>
        </Field>

        <Field>
          <FieldLabel>Страны-кандидаты</FieldLabel>
          <div className="flex flex-col gap-2">
            {countries.items.map((c) => (
              <label
                key={c.slug}
                className="text-c2 flex items-center gap-2 text-sm"
              >
                <input
                  type="checkbox"
                  checked={candidateCountrySlugs.includes(c.slug)}
                  onChange={() => toggleCandidate(c.slug)}
                  className="accent-gold"
                />
                {c.name}
              </label>
            ))}
          </div>
          {candidateCountrySlugs.length === 0 && (
            <p
              role="alert"
              className="text-terra3 text-sm"
            >
              Выберите хотя бы одну страну-кандидат.
            </p>
          )}
        </Field>

        <Field>
          <FieldLabel htmlFor="scenario-select">Сценарий</FieldLabel>
          {noScenariosAvailable ? (
            <p
              role="alert"
              className="text-terra3 text-sm"
            >
              Готовые сценарии подбора пока отсутствуют.
            </p>
          ) : (
            <select
              id="scenario-select"
              className="border-warm bg-bg2 text-c2 focus-visible:border-gold w-full border px-3 py-2 text-sm outline-none"
              value={scenarioSlug}
              onChange={(e) => setScenarioSlug(e.target.value)}
              data-testid="decision-scenario-select"
            >
              {decisionReadyScenarios.map((s) => (
                <option
                  key={s.slug}
                  value={s.slug}
                >
                  {s.name}
                </option>
              ))}
            </select>
          )}
        </Field>

        <Field>
          <FieldLabel htmlFor="persona-select">Персона</FieldLabel>
          <select
            id="persona-select"
            className="border-warm bg-bg2 text-c2 focus-visible:border-gold w-full border px-3 py-2 text-sm outline-none"
            value={selectedPersonaSlug}
            onChange={(e) => {
              const personaSlug = e.target.value;
              setSelectedPersonaSlug(personaSlug);
              if (personaSlug) {
                trackAnalyticsEvent({
                  event_type: "persona_selected",
                  source: "web",
                  persona_slug: personaSlug,
                });
              }
            }}
            data-testid="persona-selector"
          >
            <option value="">Без персонализации</option>
            {(personas?.items ?? []).map((persona) => (
              <option
                key={persona.slug}
                value={persona.slug}
              >
                {persona.name}
              </option>
            ))}
          </select>
          <p className="text-c4 text-xs">
            Рейтинг будет адаптирован под выбранный профиль.
          </p>
        </Field>

        <DecisionWeightSliders
          weights={customWeights}
          onChange={handleWeightChange}
          onReset={handleWeightReset}
        />

        <Button
          onClick={handleRun}
          disabled={
            runDecision.isPending ||
            candidateCountrySlugs.length === 0 ||
            noScenariosAvailable ||
            customWeightsBlocked
          }
          aria-busy={runDecision.isPending}
          data-testid="decision-run-button"
        >
          {runDecision.isPending ? "Выполняется подбор…" : "Запустить подбор"}
        </Button>
      </Card>

      <div className="flex flex-col gap-6">
        {!runDecision.isPending && resolvedRunError !== null && (
          <ErrorState error={resolvedRunError} />
        )}
        {!runDecision.isPending &&
          resolvedRunError === null &&
          result === null && (
            <EmptyState message="Выберите сценарий и запустите подбор, чтобы увидеть рейтинг." />
          )}
        {result !== null && <DecisionResults response={result} />}
        {result !== null && lastDecisionRequest !== null && (
          <DecisionPassportActions
            decisionRequest={lastDecisionRequest}
            locale={locale}
          />
        )}
        {result !== null && candidateCountrySlugs.length === 2 && (
          <DecisionCiiComparison
            countrySlugs={candidateCountrySlugs}
            scenarioSlug={scenarioSlug}
            locale={locale}
            personaSlug={selectedPersonaSlug || result.applied_persona?.slug}
          />
        )}
        {result !== null && (
          <DecisionRiskContext
            countrySlugs={candidateCountrySlugs}
            scenarioSlug={scenarioSlug}
            locale={locale}
          />
        )}
      </div>
    </div>
  );
}

export function DecisionRunForm() {
  return (
    <Suspense fallback={<LoadingState message="Загрузка формы подбора…" />}>
      <DecisionFormInner />
    </Suspense>
  );
}
