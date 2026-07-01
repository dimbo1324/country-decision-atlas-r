"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

import type { CountryListResponse } from "../../shared/api/countries";
import type { ScenarioListResponse } from "../../shared/api/scenarios";
import type { DecisionRunResponse } from "../../shared/api/decision";
import type { PersonaListResponse } from "../../shared/api/personas";
import { countriesApi, scenariosApi, decisionApi, personasApi } from "../../shared/api";
import { trackEvent } from "../../shared/analytics/client";
import { normalizeLocale } from "../../shared/lib/locale";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";
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

type RunError = { error?: { code?: string; message?: string } } | string | null;

const DECISION_PERSONALIZATION_ERROR_MESSAGES: Record<string, string> = {
  unknown_custom_weight_criterion: "Проверьте значения приоритетов.",
  custom_weights_incomplete: "Проверьте значения приоритетов.",
  custom_weight_out_of_range: "Проверьте значения приоритетов.",
  custom_weight_invalid: "Проверьте значения приоритетов.",
  custom_weights_sum_zero: "Сумма приоритетов должна быть больше нуля.",
  decision_personalization_disabled: "Настройка приоритетов временно недоступна.",
};

function DecisionFormInner() {
  const searchParams = useSearchParams();
  const locale = normalizeLocale(searchParams.get("locale"));

  const [countries, setCountries] = useState<CountryListResponse | null>(null);
  const [scenarios, setScenarios] = useState<ScenarioListResponse | null>(null);
  const [personas, setPersonas] = useState<PersonaListResponse | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [originCountrySlug, setOriginCountrySlug] = useState("russia");
  const [candidateCountrySlugs, setCandidateCountrySlugs] = useState<string[]>([
    "russia",
    "uruguay",
  ]);
  const [scenarioSlug, setScenarioSlug] = useState<string>(
    DEFAULT_DECISION_READY_SCENARIO_SLUG,
  );
  const [selectedPersonaSlug, setSelectedPersonaSlug] = useState("");

  const [customWeights, setCustomWeights] = useState<Record<DecisionCriterion, number>>(
    {
      ...DEFAULT_DECISION_WEIGHTS,
    },
  );
  const [personalizationTouched, setPersonalizationTouched] = useState(false);

  const [result, setResult] = useState<DecisionRunResponse | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [runError, setRunError] = useState<RunError>(null);

  useEffect(() => {
    let cancelled = false;
    setLoadError(null);

    Promise.all([
      countriesApi.listCountries({ locale }),
      scenariosApi.listScenarios({ locale }),
    ])
      .then(([c, s]) => {
        if (!cancelled) {
          setCountries(c);
          setScenarios(s);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setLoadError(
            err instanceof Error ? err.message : "Не удалось загрузить данные",
          );
        }
      });

    return () => {
      cancelled = true;
    };
  }, [locale]);

  useEffect(() => {
    let cancelled = false;
    setPersonas(null);

    personasApi
      .listPersonas(locale)
      .then((res) => {
        if (!cancelled) {
          setPersonas(res);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setPersonas({
            items: [],
            locale: {
              requested_locale: locale,
              resolved_locale: locale,
              translation_status: "missing",
            },
          });
          setSelectedPersonaSlug("");
        }
      });

    return () => {
      cancelled = true;
    };
  }, [locale]);

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

  const customWeightsSum = DECISION_CRITERIA_ORDER.reduce(
    (total, criterion) => total + customWeights[criterion],
    0,
  );
  const customWeightsBlocked = personalizationTouched && customWeightsSum === 0;

  async function handleRun() {
    if (candidateCountrySlugs.length === 0) return;
    if (customWeightsBlocked) return;
    void trackEvent({
      event_type: "decision_started",
      source: "web",
      path: "/decision",
      locale,
      scenario_slug: scenarioSlug,
      persona_slug: selectedPersonaSlug || undefined,
      metadata: {
        candidate_count: candidateCountrySlugs.length,
      },
    });
    setIsRunning(true);
    setRunError(null);
    setResult(null);
    try {
      const res = await decisionApi.runDecision({
        origin_country_slug: originCountrySlug,
        candidate_country_slugs: candidateCountrySlugs,
        scenario_slug: scenarioSlug,
        locale,
        ...(selectedPersonaSlug ? { persona: selectedPersonaSlug } : {}),
        ...(personalizationTouched ? { custom_weights: customWeights } : {}),
      });
      setResult(res);
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
    } finally {
      setIsRunning(false);
    }
  }

  if (loadError) return <ErrorState error={loadError} />;
  if (!countries || !scenarios) {
    return <LoadingState message="Загрузка стран и сценариев…" />;
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
    <div className="decisionLayout">
      <div className="decisionForm">
        <DecisionWizard
          locale={locale}
          countries={countries}
          originCountrySlug={originCountrySlug}
          onApply={handleWizardApply}
        />

        <div className="formGroup">
          <label className="formLabel" htmlFor="origin-select">
            Страна отправления
          </label>
          <select
            id="origin-select"
            className="formSelect"
            value={originCountrySlug}
            onChange={(e) => setOriginCountrySlug(e.target.value)}
          >
            {countries.items.map((c) => (
              <option key={c.slug} value={c.slug}>
                {c.name}
              </option>
            ))}
          </select>
        </div>

        <div className="formGroup">
          <label className="formLabel">Страны-кандидаты</label>
          <div className="checkboxList">
            {countries.items.map((c) => (
              <label key={c.slug} className="checkboxLabel">
                <input
                  type="checkbox"
                  checked={candidateCountrySlugs.includes(c.slug)}
                  onChange={() => toggleCandidate(c.slug)}
                />
                {c.name}
              </label>
            ))}
          </div>
          {candidateCountrySlugs.length === 0 && (
            <p className="formError" role="alert">
              Выберите хотя бы одну страну-кандидат.
            </p>
          )}
        </div>

        <div className="formGroup">
          <label className="formLabel" htmlFor="scenario-select">
            Сценарий
          </label>
          {noScenariosAvailable ? (
            <p className="formError" role="alert">
              Готовые сценарии подбора пока отсутствуют.
            </p>
          ) : (
            <select
              id="scenario-select"
              className="formSelect"
              value={scenarioSlug}
              onChange={(e) => setScenarioSlug(e.target.value)}
              data-testid="decision-scenario-select"
            >
              {decisionReadyScenarios.map((s) => (
                <option key={s.slug} value={s.slug}>
                  {s.name}
                </option>
              ))}
            </select>
          )}
        </div>

        <div className="formGroup">
          <label className="formLabel" htmlFor="persona-select">
            Персона
          </label>
          <select
            id="persona-select"
            className="formSelect"
            value={selectedPersonaSlug}
            onChange={(e) => {
              const personaSlug = e.target.value;
              setSelectedPersonaSlug(personaSlug);
              if (personaSlug) {
                void trackEvent({
                  event_type: "persona_selected",
                  source: "web",
                  path: "/decision",
                  locale,
                  persona_slug: personaSlug,
                });
              }
            }}
            data-testid="persona-selector"
          >
            <option value="">Без персонализации</option>
            {(personas?.items ?? []).map((persona) => (
              <option key={persona.slug} value={persona.slug}>
                {persona.name}
              </option>
            ))}
          </select>
          <p className="formHint">Рейтинг будет адаптирован под выбранный профиль.</p>
        </div>

        <DecisionWeightSliders
          weights={customWeights}
          onChange={handleWeightChange}
          onReset={handleWeightReset}
        />

        <button
          className="runButton"
          onClick={handleRun}
          disabled={
            isRunning ||
            candidateCountrySlugs.length === 0 ||
            noScenariosAvailable ||
            customWeightsBlocked
          }
          aria-busy={isRunning}
          data-testid="decision-run-button"
        >
          {isRunning ? "Выполняется подбор…" : "Запустить подбор"}
        </button>
      </div>

      <div>
        {isRunning && <LoadingState message="Выполняется движок подбора…" />}
        {!isRunning && resolvedRunError !== null && (
          <ErrorState error={resolvedRunError} />
        )}
        {!isRunning && resolvedRunError === null && result === null && (
          <EmptyState message="Выберите сценарий и запустите подбор, чтобы увидеть рейтинг." />
        )}
        {result !== null && <DecisionResults response={result} />}
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
